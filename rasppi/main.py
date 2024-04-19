import subprocess
import re
import socket
import pickle
import struct
import RPi.GPIO as GPIO
import time
import os

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin
gpio_pin = 26

# Setup the GPIO pin as input with pull-up resistor
GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def capture_image():
    # Use raspistill command to capture an image and store it as img.png
    subprocess.run(["raspistill", "-o", "img.png"])

def get_device_ip(mac_address):
    # Convert the MAC address to lowercase and replace hyphens with colons
    mac_address = mac_address.lower().replace('-', ':')
    print("My MAC address:", mac_address)  # Debugging information
    
    # Execute the arp -a command to get the list of devices in the network
    print("Getting device IP...")
    arp_output = subprocess.check_output(["arp", "-a"]).decode()
    print("ARP output:", arp_output)  # Debugging information
    
    # Split the ARP output into lines and iterate through each line
    for line in arp_output.split('\n'):
        # Check if the MAC address is in the line
        if mac_address in line:
            # Extract the IP address using a regular expression
            ip_address_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
            if ip_address_match:
                return ip_address_match.group(1)
    
    # If no matching IP address is found
    print("Device with the specified MAC address not found in the network.")
    return None



def send_image_and_receive_text(ip_address):
    if ip_address is None:
        print("Device with the specified MAC address not found in the network.")
        return

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 55001
    try:
        client_socket.connect((ip_address, port))
        print("Connected to the device at IP:", ip_address)

        # Open and send the image file to the server
        with open("tab.png", "rb") as img_file:
            image_data = img_file.read()
            client_socket.sendall(struct.pack("Q", len(image_data)) + image_data)
            print("Image sent to server")

        # Receive the text from the server
        received_text = client_socket.recv(4096).decode()
        print("Received text from server:", received_text)

    except Exception as e:
        print("Error:", e)
    finally:
        client_socket.close()

if __name__ == "__main__":
    try:
        while True:
            # Read the GPIO pin state
            gpio_state = GPIO.input(gpio_pin)
            print("stared the code..")
            print(gpio_state)
            # Check if the GPIO pin is low
            if gpio_state == GPIO.LOW:
                print("GPIO pin is LOW. Capturing and sending image...")
                
                # Check if img.png already exists, if yes, delete it
                # if os.path.exists("img.png"):
                #     os.remove("img.png")
                
                # Capture a new image
                # capture_image()
                
                # Find the IP address associated with the specified MAC address
                mac_address = "C0-A5-E8-6F-94-E7"
                
                ip_address = get_device_ip(mac_address)
                
                
                # Send the captured image to the device with the specified MAC address
                send_image_and_receive_text(ip_address)
                
                # break  # Exit the loop after capturing and sending the image

            # Wait for a short time before reading again
            time.sleep(1)

    except KeyboardInterrupt:
        print("Exiting...")

    finally:
        # Cleanup GPIO
        GPIO.cleanup()
