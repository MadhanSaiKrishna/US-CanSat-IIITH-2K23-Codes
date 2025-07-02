import board
from time import sleep
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


def init():
	i2c = busio.I2C(board.SCL,board.SDA)
	sensor = ADS.ADS1115(i2c)

	return sensor


def readChannel1():
	ads = init()
	channel1 = AnalogIn(ads, ADS.P0)

	voltage = channel1.voltage

	return voltage


def readChannel2():
	ads = init()
	channel2 = AnalogIn(ads, ADS.P1)

	voltage = channel2.voltage

	return voltage


def testModule():
	voltage1 = readChannel1()
	voltage2 = readChannel2()
	print("Voltage 1: ", voltage1, "Voltage 2: ", voltage2)


if __name__ == "__main__":
	while True:
		testModule()
		sleep(1)
