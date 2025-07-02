import RPi.GPIO as GPIO
import time

DATA_PIN = 24  # GPIO pin for data
CLOCK_PIN = 23  # GPIO pin for clock
CLOCK_WAIT_TIME = 0.01

GPIO.setmode(GPIO.BCM)
GPIO.setup(DATA_PIN, GPIO.OUT)
GPIO.setup(CLOCK_PIN, GPIO.OUT)


def send_bit(bit):
    GPIO.output(DATA_PIN, bit)
    time.sleep(CLOCK_WAIT_TIME)
    GPIO.output(CLOCK_PIN, 1)
    time.sleep(CLOCK_WAIT_TIME)
    GPIO.output(CLOCK_PIN, 0)
    time.sleep(CLOCK_WAIT_TIME)


def send_message(message):
    for char in message:
        binary = format(ord(char), '08b')
        for bit in binary:
            send_bit(int(bit))


try:
    while True:
        message = input("Enter a message: ")
        send_message(message)
except KeyboardInterrupt:
    GPIO.cleanup()
