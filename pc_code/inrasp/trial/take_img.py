import subprocess
import socket
import pickle
import struct

def receive_image_and_send_text():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "Raspberrypi.local"  
    port = 55001
    try:
        client_socket.connect((host, port))
        print("Connected to Raspberry Pi")

        # Open and send the image file to the client
        with open("img.png", "rb") as img_file:
            image_data = img_file.read()
            client_socket.sendall(struct.pack("Q", len(image_data)) + image_data)
            print("Image sent to client")

        # Receive the text from the client
        received_text = client_socket.recv(4096).decode()
        print("Received text from client:", received_text)

    except Exception as e:
        print("Error:", e)
    finally:
        client_socket.close()

if __name__ == "__main__":
    receive_image_and_send_text()


