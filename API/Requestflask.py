import requests
import cv2 
import os
def capture_image():
    # vid = cv2.VideoCapture("https://192.168.134.231:8080/video")
    vid = cv2.VideoCapture(0)
    ret, frame = vid.read() 
    cv2.imwrite("test.jpg",frame)
    return

def delete_image():
    os.remove("test.jpg")
    return

def image_to_be_sent():
    # file_name=file
    resp = requests.post("http://localhost:5000/predict",data={'Mode':'OCR'},files={'file':open('test.jpg','rb')})
    return resp


capture_image()#first take image from raspberri
resp=image_to_be_sent()#then send the image through api and wait for responce
print(resp.json())
delete_image()#delete the image once it is sent coz it could eat space