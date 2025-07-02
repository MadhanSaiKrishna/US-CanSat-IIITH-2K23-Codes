from smbus2 import SMBus
import time
import math
from typing import List

MS4525D0_ADDRESS = 0x28

class MS4525DO_Sensor:
	"""
	Class for MS4525DO sensor.
	"""

	def __init__(self):
		"""
		Class constructor. Instantiates the :class:`MS4525DO_Sensor`
		with the required properties.
		"""
		# Initialise bus.
		self._bus = SMBus(1)

		# Define other values.
		self._pressure: float = None
		self._air_speed: float = None

		return
	
	def _get_pressure(self) -> float:
		"""
		Reads the pressure value from the sensor data and
		stores the value in the :class:`MS4525DO_Sensor` object.

		Returns:
			`pressure`: Pressure value.
		"""
		pressure = self._bus.read_byte(MS4525D0_ADDRESS)

		self._pressure = pressure
		return pressure

	def pressure(self) -> float:
		"""
		Returns:
			`pressure`: MS4525DO Pressure value.
		"""
		return self._pressure
	
	def _calc_air_speed(self) -> float:
		"""
		Calculates the air speed value from the sensor data and
		stores the value in the :class:`MS4525DO_Sensor` object.

		Returns:
			`air_speed`: Air speed value.
		"""
		pressure = self._get_pressure()
		air_speed = math.sqrt(pressure / (2 * 1.225))

		self._air_speed = air_speed
		return air_speed

	def air_speed(self) -> float:
		"""
		Returns:
			`air_speed`: MS4525DO Air speed value.
		"""
		return self._air_speed
	
	def read_values(self) -> List[float]:
		"""
		Calculates the pressure and air speed from the sensor data
		and stores the value in the :class:`MS4525DO_Sensor` object.

		Returns:
			`[temperature, air_speed]`: List containing the pressure
			 and air speed values.
		"""
		# Calculate sensor values.
		self._calc_air_speed()

		# Return calculated values.
		return self.pressure(), self.air_speed()

def testModule():
	sensor = MS4525DO_Sensor()
	values = sensor.read_values()
	print("Pressure:", values[0], "Air Speed:", values[1])
	#print ("Air Speed = ", airSpeed)

if __name__ == "__main__":
	while True:
		testModule()
		time.sleep(1)
