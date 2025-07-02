# Distributed with a free-will license.
# Use it any way you want, profit or free, provided it fits in the licenses of its associated works.
# ADS1115
# This code is designed to work with the ADS1115_I2CADC I2C Mini Module available from ControlEverything.com.
# https://www.controleverything.com/content/Analog-Digital-Converters?sku=ADS1115_I2CADC#tabs-0-product_tabset-2

from smbus2 import SMBus
import time
from typing import List

ADS1115_ADDR = 0x48
ADS1115_WAIT_SECONDS = 1
CHANNEL_RANGE_BYTE = 0x03
CONFIGURATION_REGISTER = 0x01
READ_REGISTER = 0x00


class ADS1115_Sensor:
	"""
	Class for ADS1115 sensor.
	"""

	def __init__(self) -> None:
		"""
		Class constructor. Instantiates the :class:`ADS1115_Sensor`
		with the required properties.
		"""

		# Initialise bus.
		self._bus = SMBus(1)

		# Define other values.
		self._channel_0: float = None
		self._channel_1: float = None

		return
	
	def _read_voltage_channel_0(self) -> float:
		"""
		Calculates the channel 0 voltage value from the sensor data and
		stores the value in the :class:`ADS1115_Sensor` object.

		Returns:
			`voltage`: Channel 0 voltage value.
		"""
		data = [0xC0, 0x03]
		self._bus.write_i2c_block_data(ADS1115_ADDR, CONFIGURATION_REGISTER, data)

		data = self._bus.read_i2c_block_data(ADS1115_ADDR, READ_REGISTER, 2)

		# Convert the data
		raw_adc = data[0] * 256 + data[1]

		if raw_adc > 32767:
			raw_adc -= 65535

		raw_adc  = (raw_adc * 6.144 / 32767)

		self._channel_0 = raw_adc
		return raw_adc
	
	def _read_voltage_channel_1(self) -> float:
		"""
		Calculates the channel 1 voltage value from the sensor data and
		stores the value in the :class:`ADS1115_Sensor` object.

		Returns:
			`voltage`: Channel 1 voltage value.
		"""
		data = [0xD0, 0x03]
		self._bus.write_i2c_block_data(ADS1115_ADDR, CONFIGURATION_REGISTER, data)

		data = self._bus.read_i2c_block_data(ADS1115_ADDR, READ_REGISTER, 2)

		# Convert the data
		raw_adc = data[0] * 256 + data[1]

		if raw_adc > 32767:
			raw_adc -= 65535

		raw_adc  = (raw_adc * 6.144 / 32767)

		self._channel_1 = raw_adc
		return raw_adc
	
	def channel_0(self) -> float:
		"""
		Returns:
			`voltage`: Channel 0 voltage value.
		"""
		return self._channel_0
	
	def channel_1(self) -> float:
		"""
		Returns:
			`voltage`: Channel 1 voltage value.
		"""
		return self._channel_1
	
	def read_values(self) -> List[float]:
		"""
		Calculates the channel 0 and channel 1 voltages from the sensor data
		and stores the value in the :class:`ADS1115_Sensor` object.

		Returns:
			`[voltage, voltage]`: List comtaining the voltage of channel 0 and 1.
		"""
		self._read_voltage_channel_0()
		time.sleep(ADS1115_WAIT_SECONDS)
		self._read_voltage_channel_1()

		return self.channel_0(), self.channel_1()


if __name__ == "__main__":
	sensor = ADS1115_Sensor()
	while True:
		values = sensor.read_values()
		print("Channel 0:", values[0])
		print("Channel 1:", values[1])
		time.sleep(1)
