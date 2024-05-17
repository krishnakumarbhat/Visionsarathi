import subprocess
import re
import socket
import struct
import RPi.GPIO as GPIO
import time
import os
import pygame

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define the GPIO pins
gpio_pin_capture = 26
gpio_pin_sound = 21  # Connected to Amp DIN

# Setup the GPIO pins
GPIO.setup(gpio_pin_capture, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(gpio_pin_sound, GPIO.OUT)

def capture_image():
    """Capture an image using fswebcam and save it as img.png."""
    # Use raspistill command to capture an image and store it as img.png
    # subprocess.run(["raspistill", "-o", "img.png"])
    # subprocess.run(["fswebcam -r 1280x720 --no-banner","img.png"])

    # Run the command using os.system
    os.system("fswebcam -r 640x480 -b MJPEG --no-banner img.png")

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

def recv_msg(sock):
    """Receive a message from the socket."""
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    return recvall(sock, msglen)

def recvall(sock, n):
    """Receive n bytes from the socket."""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


def send_image_and_receive_audio(ip_address):
    """Send an image to the server and receive audio in response."""
    if ip_address is None:
        print("Device with the specified MAC address not found in the network.")
        return

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 55001
    try:
        client_socket.connect((ip_address, port))
        print("Connected to the device at IP:", ip_address)

        # Open and send the image file to the server
        with open("img.png", "rb") as img_file:
            image_data = img_file.read()
            client_socket.sendall(struct.pack("Q", len(image_data)) + image_data)
            print("Image sent to server")

        # Receive the audio from the server
        received_data = recv_msg(client_socket)

        # Handle audio format (replace with your specific format)
        audio_format = "mp3"
        audio_file_path = f"audio.{audio_format}"
        with open(audio_file_path, "wb") as audio_file:
            audio_file.write(received_data)
        print(f"Received audio data (format: {audio_format})")
        
        return audio_file_path

    except Exception as e:
        print("Error:", e)
    finally:
        client_socket.close()

def play_audio(music_file_path):
    """Play the audio file."""
    pygame.mixer.init()
    pygame.mixer.music.load(music_file_path)
    pygame.mixer.music.set_volume(0.7)
    pygame.mixer.music.play()
    # while pygame.mixer.music.get_busy():
    #     continue
    while pygame.mixer.music.get_busy():
        time.sleep(1)



def main():
    try:
        while True:
            gpio_state_capture = GPIO.input(gpio_pin_capture)
            gpio_state_sound = GPIO.input(gpio_pin_sound)

            if gpio_state_capture == GPIO.LOW:
                print("GPIO pin is LOW. Capturing and sending image...")
                # capture_image()

                mac_address = "C0-A5-E8-6F-94-E7"
                ip_address = get_device_ip(mac_address)

                audio_file_path = send_image_and_receive_audio(ip_address)

            if gpio_state_sound == GPIO.LOW:
                print("GPIO pin is LOW. Playing sound...")
                play_audio("audio.mp3")

            time.sleep(1)

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
