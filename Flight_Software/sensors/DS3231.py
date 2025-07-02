from smbus2 import SMBus
import time
from typing import List

DS3231_ADDRESS = 0x68

class DS3231_Sensor:
	"""
	Class for DS3231 sensor.
	"""

	def __init__(self):
		"""
		Class constructor. Instantiates the :class:`DS3231_Sensor`
		with the required properties.
		"""
		# Initialise bus.
		self._bus = SMBus(1)
		# Configure the device.
		# self._bus.write_byte_data(0x77, 0x1B, 0x13)
		# while self._bus.read_byte_data(0x77, 0x03) & 0x60 != 0x60:
		# 	time.sleep(0.001)

		# Define other values.
		self._raw_time: List[int] = None
		self._seconds: int = None
		self._minutes: int = None
		self._hours: int = None
		self._day: int = None
		self._week: int = None
		self._month: int = None
		self._year: int = None
		self.telemetry_time: str = None

		return
	
	def _read_time(self) -> List[int]:
		time1 = self._bus.read_i2c_block_data(DS3231_ADDRESS, 0x00, 9)
		self._seconds = time1[0]
		self._minutes = time1[1]
		self._hours = time1[2]
		self._day = time1[3]
		self._week = time1[4]
		self._month = time1[5]
		self._year = time1[6]

		self._raw_time = time1
		return time1
	
	def _bcd_to_int(bcd, n = 2):
		return int(('%x' % bcd)[-n:])
	
	def _get_telemetry_time(self) -> str:
		self._read_time()
		time_tel = tuple(self._bcd_to_int(t) for t in(self._raw_time))
		self.telemetry_time = time_tel
		return time_tel
	
	def read_values(self) -> tuple[List[int], str]:
		telemetry = self._get_telemetry_time()
		raw = self._raw_time
		return raw, telemetry

# def bcd_to_int(bcd, n=2):
# 	return int(('%x' % bcd)[-n:])

# def int_to_bcd(x,n=2):
# 	return int(str(x)[-n:], 0x10)

# bus = SMBus(1)

# time1 = bus.read_i2c_block_data(DS3231_ADDRESS, 0x00, 9)


# seconds = time1[0]
# minutes = time1[1]
# hours = time1[2]
# day = time1[3]
# week = time1[4]
# month = time1[5]
# year = time1[6]

# a = tuple(bcd_to_int(t) for t in(year,month,week,day,hours,minutes,seconds))

#print (time1[0])
if __name__ == "__main__":
	sensor = DS3231_Sensor()
	while True:
		print(sensor.get_telemetry_time())
		print (time.strftime('%H:%M:%S'))
