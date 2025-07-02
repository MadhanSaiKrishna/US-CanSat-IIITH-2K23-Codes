from smbus2 import SMBus
import time

AHT21B_Address = 0x38

## data = bus.read_byte(0x38)
## print (data)

class AHT21B_Sensor:
	"""
	Class for AHT21B sensor.
	"""

	def __init__(self) -> None:
		"""
		Class constructor. Instantiates the :class:`AHT21B_Sensor`
		with the required properties.
		"""

		# Initialise bus.
		self._bus = SMBus(1)

		# Define other values.
		self._temperature: float = None

		return
	
	def temperature(self) -> float:
		"""
		Returns:
			`temperature`: AHT21B Temperature value.
		"""
		return self._temperature
	
	def read_value(self) -> float:
		"""
		Calculates the temperature value from the sensor data and
		stores the value in the :class:`AHT21B_Sensor` object.

		Returns:
			`temperature`: Temperature value.
		"""
		self._bus.write_i2c_block_data(0x38, 0x70, [0xAC, 0x33, 0x00])
		data = self._bus.read_i2c_block_data(0x38, 0x71, 7)

		# Calculate temperature value.
		temperature = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[3]
		temperature = ((200 * temperature) / 1048576) - 50

		# Store temperature.
		self._temperature = temperature

		# Return temperature.
		return temperature


if __name__ == "__main__":
	sensor = AHT21B_Sensor()
	while True:
		print(sensor.read_value())
		time.sleep(1)
