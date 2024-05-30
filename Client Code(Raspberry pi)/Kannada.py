import time
import pygame
print("playing kan")
pygame.mixer.init()
pygame.mixer.music.load('audio_kan.mp3')
pygame.mixer.music.set_volume(0.7)
pygame.mixer.music.play()
while pygame.mixer.music.get_busy():
     continue

