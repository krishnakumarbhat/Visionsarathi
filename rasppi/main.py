import subprocess
import re
import socket
import pickle
import struct
import RPi.GPIO as GPIO
import time
import wave
import pyaudio
import os

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define the GPIO pins
gpio_pin_capture = 26
gpio_pin_sound = 14  # Connected to Amp DIN

# Setup the GPIO pins
GPIO.setup(gpio_pin_capture, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(gpio_pin_sound, GPIO.OUT)

def capture_image():
    """Capture an image using fswebcam."""
    subprocess.run(["fswebcam", "-r", "640x480", "-b", "MJPEG", "--no-banner", "img.png"])

def get_device_ip(mac_address):
    """Get the IP address associated with a given MAC address."""
    mac_address = mac_address.lower().replace('-', ':')
    arp_output = subprocess.check_output(["arp", "-a"]).decode()
    for line in arp_output.split('\n'):
        if mac_address in line:
            ip_address_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
            if ip_address_match:
                return ip_address_match.group(1)
    return None

def send_image_and_receive_audio(ip_address):
    """Send captured image to the specified IP address and receive audio."""
    if ip_address is None:
        print("Device with the specified MAC address not found in the network.")
        return

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 55001
    try:
        client_socket.connect((ip_address, port))
        print("Connected to the device at IP:", ip_address)

        with open("img.png", "rb") as img_file:
            image_data = img_file.read()
            client_socket.sendall(struct.pack("Q", len(image_data)) + image_data)
            print("Image sent to server")

        # Receive audio data
        audio_data = b''
        while True:
            packet = client_socket.recv(4096)
            if not packet:
                break
            audio_data += packet

        return audio_data

    except Exception as e:
        print("Error:", e)
    finally:
        client_socket.close()

def save_audio(audio_data, file_path):
    """Save received audio data as a WAV file."""
    with open(file_path, 'wb') as audio_file:
        audio_file.write(audio_data)
    print("Audio saved to:", file_path)

def play_audio(file_path):
    """Play audio using PyAudio."""
    if os.path.exists(file_path):
        CHUNK = 1024

        wf = wave.open(file_path, 'rb')

        # Instantiate PyAudio
        p = pyaudio.PyAudio()

        # Open stream
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        # Read data
        data = wf.readframes(CHUNK)

        # Play the sound
        while data:
            stream.write(data)
            data = wf.readframes(CHUNK)

        # Stop stream
        stream.stop_stream()
        stream.close()

        # Close PyAudio
        p.terminate()
    else:
        print("Audio file not found.")

def main():
    try:
        while True:
            gpio_state_capture = GPIO.input(gpio_pin_capture)
            gpio_state_sound = GPIO.input(gpio_pin_sound)

            print("GPIO state (capture):", gpio_state_capture)
            print("GPIO state (sound):", gpio_state_sound)

            if gpio_state_capture == GPIO.LOW:
                print("GPIO pin is LOW. Capturing and sending image...")
                capture_image()

                mac_address = "C0-A5-E8-6F-94-E7"
                ip_address = get_device_ip(mac_address)

                audio_data = send_image_and_receive_audio(ip_address)

                # Save received audio data
                audio_file_path = "audio.wav"
                save_audio(audio_data, audio_file_path)

            if gpio_state_sound == GPIO.LOW:
                print("GPIO pin is LOW. Playing sound...")
                play_audio("audio.wav")

            time.sleep(1)

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
