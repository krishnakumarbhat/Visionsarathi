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
gpio_pin_capture = 6

# Setup the GPIO pins
GPIO.setup(gpio_pin_capture, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def capture_image():
    """Capture an image using fswebcam and save it as img.png."""
    os.system("raspistill -o img.png")

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
    """Send an image to the server and receive two audio files in response."""
    if ip_address is None:
        print("Device with the specified MAC address not found in the network.")
        return

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 52001
    try:
        client_socket.connect((ip_address, port))
        print("Connected to the device at IP:", ip_address)

        # Open and send the image file to the server
        with open("img.png", "rb") as img_file:
            image_data = img_file.read()
            client_socket.sendall(struct.pack("Q", len(image_data)) + image_data)
            print("Image sent to server")

        # Receive the first audio file from the server
        received_data1 = recv_msg(client_socket)
        audio_file_path1 = "audio.mp3"
        with open(audio_file_path1, "wb") as audio_file1:
            audio_file1.write(received_data1)
        print(f"Received first audio file: {audio_file_path1}")

        # Receive the second audio file from the server
        received_data2 = recv_msg(client_socket)
        audio_file_path2 = "audio_kan.mp3"
        with open(audio_file_path2, "wb") as audio_file2:
            audio_file2.write(received_data2)
        print(f"Received second audio file: {audio_file_path2}")
        return audio_file_path1, audio_file_path2

    except Exception as e:
        print("Error:", e)
    finally:
        client_socket.close()

def main():
    try:
        while True:
            gpio_state_capture = GPIO.input(gpio_pin_capture)
            if gpio_state_capture == GPIO.LOW:
                print("GPIO pin is LOW. Capturing and sending image...")
                capture_image()
                mac_address = "C0-A5-E8-6F-94-E7"
                ip_address = get_device_ip(mac_address)
                audio_file_paths = send_image_and_receive_audio(ip_address)
                if audio_file_paths:
                    for audio_file_path in audio_file_paths:
                        print(f"Audio file saved: {audio_file_path}")
                os.system("python ean.py")

            time.sleep(1)

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        print("in finally")
        GPIO.cleanup()

if __name__ == "__main__":
    main()

