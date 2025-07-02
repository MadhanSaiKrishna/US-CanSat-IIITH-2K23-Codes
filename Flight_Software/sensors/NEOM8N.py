import serial
import time
import string
#import pynmea2

while True:
	port="/dev/serial0"
	ser = serial.Serial(port,baudrate=9600,timeout=5)
	#dataout = pynmea2.NMEAStreamReader()
	newdata = ser.readline()
	print (newdata)
