import time
import pygame
print("audio recived and en audio is playing...")
pygame.mixer.init()
pygame.mixer.music.load('audio.mp3')
pygame.mixer.music.set_volume(0.7)
pygame.mixer.music.play()
while pygame.mixer.music.get_busy():
     continue
