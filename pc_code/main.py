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
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    port = 52001
    server_socket.bind((ip, port))
    server_socket.listen(5)
    print(f"Server started at {ip}:{port}")
    
    while True:
        print("Waiting for client connection...")
        client_socket, addr = server_socket.accept()
        try:
            num = read_num_from_file("num.txt")
            image_data = receive_image(client_socket)
            img_path = save_image(image_data, num)
            increment_num_in_file("num.txt", num)
            process_image_and_send_audio(img_path, client_socket)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()

def read_num_from_file(filename):
    """Read a number from a file."""
    try:
        with open(filename, "r") as file:
            return int(file.read())
    except FileNotFoundError:
        return 0

def increment_num_in_file(filename, num):
    """Increment the number in a file."""
    with open(filename, "w") as file:
        file.write(str(num + 1))

def receive_image(sock):
    """Receive an image from the socket."""
    data = b""
    payload_size = struct.calcsize("Q")
    while len(data) < payload_size:
        data += sock.recv(4096)
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("Q", packed_msg_size)[0]
    while len(data) < msg_size:
        data += sock.recv(4096)
    return data[:msg_size]

def save_image(image_data, num):
    """Save image data to a file."""
    img_path = f"img{num}.png"
    with open(img_path, "wb") as img_file:
        img_file.write(image_data)
    print(f"Image saved as {img_path}")
    return img_path

def process_image_and_send_audio(img_path, client_socket):
    """Process the image, generate a caption and OCR text, convert to speech, and send audio back to the client."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    image_size = 384
    global image_caption, ocr_text

    raw_image = Image.open(img_path).convert('RGB')
    transform = get_image_transform(image_size)
    image = transform(raw_image).unsqueeze(0).to(device)

    model = load_captioning_model(device, image_size)
    image_caption = generate_image_caption(model, image)

    ocr_text = perform_ocr(img_path)
    combined_text = combine_caption_and_ocr(image_caption, ocr_text)
    processed_text = process_text_with_ollama(combined_text)
    print(f"llama3:{processed_text}")
    audio_data = text_to_speech(processed_text)
    send_audio_to_client(audio_data, client_socket)

def get_image_transform(image_size):
    """Get image transformation pipeline."""
    return transforms.Compose([
        transforms.Resize((image_size, image_size), interpolation=InterpolationMode.BICUBIC),
        transforms.ToTensor(),
        transforms.Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711))
    ])

def load_captioning_model(device, image_size):
    """Load and initialize the image captioning model."""
    model_url = '../model.pth'
    model = blip_decoder(pretrained=model_url, image_size=image_size, vit='base')
    model.eval()
    return model.to(device)

def generate_image_caption(model, image):
    """Generate a caption for the image."""
    with torch.no_grad():
        caption = model.generate(image, sample=False, num_beams=3, max_length=35, min_length=11)
    return caption[0]

def perform_ocr(img_path):
    """Perform OCR on the image."""
    reader = easyocr.Reader(['en'])
    ocr_result = reader.readtext(img_path)
    return "\n".join([detection[1] for detection in ocr_result])

def combine_caption_and_ocr(image_caption, ocr_text):
    """Combine the image caption and OCR text."""
    print(f"IM : {image_caption} and OCR: {ocr_text}")
    return f"Image Caption:\n{image_caption}\n\nOCR Text:\n{ocr_text}"

def process_text_with_ollama(text):
    """Process the combined text with Ollama."""
    prompt = (f"This is image captioning output with OCR in it. "
              f"Can you describe it properly (without any spelling errors) for a blind person within 19 words? "
              f"[(imagecap: {image_caption} and ocrtext: {ocr_text})]")
    llm = Ollama(model="llama3")
    print("running llama3 ... ")
    return llm.invoke(prompt)

def text_to_speech(text):
    """Convert text to speech and return the audio data."""
    tts = gTTS(text=text, lang='en')
    audio_data = io.BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)
    return audio_data.read()

def send_audio_to_client(audio_data, client_socket):
    """Send the audio data back to the client."""
    send_msg(client_socket, audio_data)
    print("Audio sent back to client")
    client_socket.close()

if __name__ == "__main__":
    receive_image_and_send_audio()
