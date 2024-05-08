# Visionsarathi
This is an innovative project aimed at enhancing the visual experience for individuals with impairments. Leveraging machine learning and natural language processing, this repository houses the codebase for generating efficient and coherent natural language descriptions of captured images. The project integrates seamlessly with image recognition, 


Overview
Visionsarathi is a project dedicated to improving the visual experience for individuals with impairments. Leveraging machine learning and natural language processing, the goal is to generate efficient and coherent natural language descriptions of captured images. The project integrates seamlessly with image recognition, offering users a unified and user-friendly interface to interact with the system.

Features
Efficient Image Descriptions: Utilize advanced NLP techniques to generate clear and concise natural language descriptions for captured images.

Unified User Experience: Integrate the NLP system seamlessly with image recognition to provide a unified and coherent experience for users.

User-Friendly Interface: Develop an accessible interface for visually impaired users, allowing them to easily prompt the system for detailed image descriptions.

Project Structure
The project structure is organized to ensure modularity and ease of understanding. Key components include:

image_processing: Contains code for image recognition and processing.
nlp_module: Implements natural language processing for generating image descriptions.




Project Report: Image Captioning and OCR with Text Optimization

Overview
The project aims to develop a system that receives images via a socket connection, processes them using an image captioning model fine-tuned on the COCO dataset, performs Optical Character Recognition (OCR) using EasyOCR, and optimizes the combined text using an Ollama large language model. The optimized text is then sent back to the client.

Technologies Used
Python: Programming language used for development.
PyTorch: Deep learning library used for image captioning model.
BLIP (Bi-directional Language-Informed Pretraining): Model architecture used for image captioning.
EasyOCR: Library used for Optical Character Recognition.
Ollama: Large language model used for text optimization.
PIL (Python Imaging Library): Library used for image processing.
Socket Programming: Used for communication between the server and client.
Struct: Used for packing and unpacking data for transmission over the network.
Implementation Details
Image Receiving and Processing
A server socket is created to listen for client connections.
Images are received in chunks and saved to disk.
Each received image is processed and sent for captioning and OCR.
Image Captioning
The saved image is preprocessed and fed into the BLIP model for caption generation.
The model generates a caption for the image.
Optical Character Recognition (OCR)
EasyOCR is used to perform OCR on the saved image.
The detected text from the OCR is extracted.
Text Optimization
The image caption and OCR text are combined into a single string.
This combined text is sent to the Ollama model for optimization.
The optimized text is then sent back to the client.
Client Communication
The processed text is sent back to the client via the socket connection.
The client receives the optimized text and can use it as needed.
Error Handling
Error handling is implemented throughout the code to handle exceptions gracefully, such as file operations, socket connections, and model loading.
Future Improvements
Implement authentication and data validation for enhanced security.
Optimize code for better performance, especially in image processing and model inference.
Enhance modularity by breaking down functions into smaller components for better maintainability.
Add logging and monitoring for better debugging and system health monitoring.
Conclusion
The project successfully demonstrates the integration of image captioning, OCR, and text optimization using state-of-the-art deep learning models and libraries. With further refinement and enhancements, it can be deployed in real-world applications, such as assisting visually impaired individuals in understanding the content of images.



