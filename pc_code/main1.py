import socket
import pickle
import struct
from PIL import Image
import torch
from torchvision import transforms
from torchvision.transforms.functional import InterpolationMode
from models.blip import blip_decoder
import easyocr

def receive_image_and_send_text():
    while True:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        ip = socket.gethostbyname(host)
        port = 55001

        try:
            server_socket.bind((ip, port))
            server_socket.listen(5)

            print("Waiting for client connection...")
            client_socket, addr = server_socket.accept()

            try:
                with open("num.txt", "r") as file:
                    num = int(file.read())
            except FileNotFoundError:
                num = 0

            data = b""
            payload_size = struct.calcsize("Q")
            while True:
                while len(data) < payload_size:
                    data += client_socket.recv(4096)
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]
                while len(data) < msg_size:
                    data += client_socket.recv(4096)
                image_data = data[:msg_size]
                data = data[msg_size:]

                with open(f"img{num}.png", "wb") as img_file:
                    img_file.write(image_data)
                    print(f"Image saved as img{num}.png")

                num += 1
                with open("num.txt", "w") as file:
                    file.write(str(num))

                process_image_and_send_text(num, client_socket)
                
        except Exception as e:
            print("Error:", e)
            client_socket.close()

def process_image_and_send_text(num, client_socket):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    image_size = 384

    img_path = f'img{num - 1}.png'
    raw_image = Image.open(img_path).convert('RGB')
    transform = transforms.Compose([
        transforms.Resize((image_size, image_size), interpolation=InterpolationMode.BICUBIC),
        transforms.ToTensor(),
        transforms.Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711))
    ])
    image = transform(raw_image).unsqueeze(0).to(device)

    # Load and initialize image captioning model
    model_url = 'model.pth'  # Replace 'model.pth' with the actual path to your pretrained model
    model = blip_decoder(pretrained=model_url, image_size=image_size, vit='base')
    model.eval()
    model = model.to(device)

    # Generate image caption
    with torch.no_grad():
        caption = model.generate(image, sample=False, num_beams=3, max_length=35, min_length=9)
        image_caption = caption[0]


    # Perform OCR
    reader = easyocr.Reader(['en'])
    ocr_result = reader.readtext(img_path)
    ocr_text = "\n".join([detection[1] for detection in ocr_result])

    # Combine image caption and OCR text
    print(image_caption)
    combined_text = f"Image Caption:\n{image_caption}\n\nOCR Text:\n{ocr_text}"

    # Send combined text back to client
    client_socket.sendall(combined_text.encode())
    print("Text sent back to client")
    client_socket.close()

if __name__ == "__main__":
    receive_image_and_send_text()
