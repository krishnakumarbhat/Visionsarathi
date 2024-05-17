import socket
import struct
from PIL import Image
import torch
from torchvision import transforms
from torchvision.transforms.functional import InterpolationMode
from models.blip import blip_decoder
import easyocr
from gtts import gTTS
import io
import os
from langchain_community.llms import Ollama

def send_msg(sock, msg):
    """Send a message through the socket."""
    msg = struct.pack(">I", len(msg)) + msg
    sock.sendall(msg)

def receive_image_and_send_audio():
    """Receive an image from the client, process it, and send back an audio response."""
    while True:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        ip = socket.gethostbyname(host)
        print(ip)
        port = 52001

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

                img_path = f"img{num}.png"
                with open(img_path, "wb") as img_file:
                    img_file.write(image_data)
                    print(f"Image saved as {img_path}")

                num += 1
                with open("num.txt", "w") as file:
                    file.write(str(num))

                process_image_and_send_audio(img_path, client_socket)

        except Exception as e:
            print("Error:", e)
        finally:
            client_socket.close()

def process_image_and_send_audio(img_path, client_socket):
    """Process the image, generate a caption and OCR text, convert to speech, and send audio back to the client."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    image_size = 384

    raw_image = Image.open(img_path).convert('RGB')
    transform = transforms.Compose([
        transforms.Resize((image_size, image_size), interpolation=InterpolationMode.BICUBIC),
        transforms.ToTensor(),
        transforms.Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711))
    ])
    image = transform(raw_image).unsqueeze(0).to(device)

    # Load and initialize image captioning model
    model_url = '../model.pth'
    model = blip_decoder(pretrained=model_url, image_size=image_size, vit='base')
    model.eval()
    model = model.to(device)

    # Generate image caption
    with torch.no_grad():
        caption = model.generate(image, sample=False, num_beams=3, max_length=35, min_length=9)
        image_caption = caption[0]

    # Perform OCR
    print("doing ocr")
    reader = easyocr.Reader(['en'])
    ocr_result = reader.readtext(img_path)
    ocr_text = "\n".join([detection[1] for detection in ocr_result])

    # Combine image caption and OCR text
    combined_text = f"Image Caption:\n{image_caption}\n\nOCR Text:\n{ocr_text}"
    print(f"before :{combined_text}")
    
    output = f"this is image captioning output with ocr in it.can you describe it poperly(without any spell error)for blind person [(imagecap:{image_caption} and ocrtext:{ocr_text})]"
    # print(output)
    print("doing ollana")
    # Invoke Ollama for text processing
    llm = Ollama(model="llama2")
    combined_text = llm.invoke(output)
    print(combined_text)
    print("hi")
    # Convert text to speech
    tts = gTTS(text=combined_text, lang='en')
    audio_data = io.BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)
    with open("output_audio.mp3", "wb") as f:
        f.write(audio_data.read())

    # Send audio data back to client
    audio_data.seek(0)
    audio_data_bytes = audio_data.read()
    send_msg(client_socket, audio_data_bytes)
    print("Audio sent back to client")
    client_socket.close()

if __name__ == "__main__":
    receive_image_and_send_audio()
