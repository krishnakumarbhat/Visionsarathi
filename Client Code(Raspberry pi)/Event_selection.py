import RPi.GPIO as GPIO
import time
import subprocess

pin_26 = 26
pin_5 = 5
pin_6 = 6

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pin_5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pin_6, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def run_script(script_name):
    subprocess.call(['python3', script_name])

try:
    while True:
        if GPIO.input(pin_26) == GPIO.LOW:
            run_script('main.py')
            # Debounce delay
            time.sleep(0.5)
        elif GPIO.input(pin_5) == GPIO.LOW:
            run_script('English_Termination.py')
            # Debounce delay
            time.sleep(0.5)
        elif GPIO.input(pin_6) == GPIO.LOW:
            run_script('kannada.py')
            # Debounce delay
            time.sleep(0.5)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()
