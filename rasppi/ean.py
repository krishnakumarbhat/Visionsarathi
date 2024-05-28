import time
import pygame
import psutil

def terminate_processes(process_names):
    # Iterate over all running processes
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            # Check if the process name matches any of the target processes
            if proc.info['name'] in process_names:
                print(f"Terminating {proc.info['name']} (PID: {proc.info['pid']})")
                proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

# List of process names to terminate
processes_to_terminate = ['main.py', 'kan.py']

# Terminate the specified processes
terminate_processes(processes_to_terminate)

print("audio received and en audio is playing...")
pygame.mixer.init()
pygame.mixer.music.load('audio.mp3')
pygame.mixer.music.set_volume(0.7)
pygame.mixer.music.play()
while pygame.mixer.music.get_busy():
    continue
