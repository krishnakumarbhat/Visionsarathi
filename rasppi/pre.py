import RPi.GPIO as GPIO
import time
import subprocess

# Pin definitions
pin_13 = 13
pin_26 = 26

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pin_26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def run_script(script_name):
    subprocess.call(['python3', script_name])

try:
    while True:
        if GPIO.input(pin_13) == GPIO.LOW:
            run_script('main.py')
            # Debounce delay
            time.sleep(0.5)
        elif GPIO.input(pin_26) == GPIO.LOW:
            run_script('siu.py')
            # Debounce delay
            time.sleep(0.5)
        time.sleep(0.1)  # Short delay to prevent excessive CPU usage
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()


