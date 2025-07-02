import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from time import sleep # Import the sleep function from the time module

beacon_pin = 5

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(beacon_pin, GPIO.OUT, initial=GPIO.LOW) # Set pin 8 to be an output pin and set initial value to low (off)

def beacon_on():
    GPIO.output(beacon_pin, GPIO.HIGH)

def beacon_off():
    GPIO.output(beacon_pin, GPIO.LOW)
    