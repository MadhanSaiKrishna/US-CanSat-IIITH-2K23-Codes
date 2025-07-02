import RPi.GPIO as GPIO
import time

DATA_PIN = 18  # GPIO pin for data
CLOCK_PIN = 23  # GPIO pin for clock

GPIO.setmode(GPIO.BCM)
GPIO.setup(DATA_PIN, GPIO.IN)
GPIO.setup(CLOCK_PIN, GPIO.IN)


def read_bit():
    while GPIO.input(CLOCK_PIN) == 0:
        pass
    bit = GPIO.input(DATA_PIN)
    while GPIO.input(CLOCK_PIN) == 1:
        pass
    return bit


def receive_message():
    message = ""
    while True:
        char_bits = ""
        for _ in range(8):
            char_bits += str(read_bit())
        if char_bits:
            message += chr(int(char_bits, 2))
            print("Received character:", chr(int(char_bits, 2)))


try:
    receive_message()
except:
    GPIO.cleanup()
