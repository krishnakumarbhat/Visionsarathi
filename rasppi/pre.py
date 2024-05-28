import RPi.GPIO as GPIO
import subprocess
import time

# Set up the GPIO mode
GPIO.setmode(GPIO.BCM)

# Define the GPIO pins
pin_ean = 5
pin_kan = 6
pin_main = 26

# Set up the GPIO pins as inputs with pull-up resistors
GPIO.setup(pin_ean, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pin_kan, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pin_main, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def run_script(script_name):
    try:
        subprocess.run(['python3', script_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running script {script_name}: {e}")

# Callback functions for each GPIO pin
def ean_callback(channel):
    print("Running ean.py")
    run_script('ean.py')

def kan_callback(channel):
    print("Running kan.py")
    run_script('kan.py')

def main_callback(channel):
    print("Running main.py")
    run_script('main.py')

# Add event detection for each GPIO pin
GPIO.add_event_detect(pin_ean, GPIO.FALLING, callback=ean_callback, bouncetime=300)
GPIO.add_event_detect(pin_kan, GPIO.FALLING, callback=kan_callback, bouncetime=300)
GPIO.add_event_detect(pin_main, GPIO.FALLING, callback=main_callback, bouncetime=300)

try:
    # Keep the script running to detect events
    print("Waiting for GPIO input...")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting program")
finally:
    # Clean up the GPIO on exit
    GPIO.cleanup()
