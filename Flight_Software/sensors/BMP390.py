from smbus2 import SMBus
import struct
import time
from typing import Any, List


class BMP390_Sensor():
	"""
	Class for BMP390 sensor.
	"""

	def __init__(self):
		"""
		Class constructor. Instantiates the :class:`BMP390_Sensor`
		with the required properties.
		"""
		# Initialise bus.
		self._bus = SMBus(1)
		# Configure the device.
		self._bus.write_byte_data(0x77, 0x1B, 0x13)
		while self._bus.read_byte_data(0x77, 0x03) & 0x60 != 0x60:
			time.sleep(0.001)

		# Define other values.
		self._coeff: tuple[Any, ...] = None
		self._data: List[int] = None
		self._temperature: float = None
		self._base_pressure: float = 1013.25
		self._pressure: float = None
		self._altitude: float = None

		return

	def _get_data(self):
		"""
		Reads the raw ADC data from the BMP390 sensor.
		"""
		# Read raw ADC data for pressure and from the sensor.
		self._data = self._bus.read_i2c_block_data(0x77, 0x04, 6)

	def _get_coeff(self):
		"""
		Reads the coefficients required to calculate the sensor values.
		"""
		# Read the coefficients required to calculate temperature and pressure.
		coeff = self._bus.read_i2c_block_data(0x77, 0x31, 21)
		# Parse the data as required.
		coeff = bytes(coeff)
		self._coeff = struct.unpack("<HHbhhbbHHbbhbb", coeff)

	def _calc_temperature(self) -> float:
		"""
		Calculates the temperature value from the sensor data and
		stores the value in the :class:`BMP390_Sensor` object.

		Returns:
			`temperature`: Temperature value.
		"""
		# Get the raw ADC data.
		self._get_data()
		# Get required coefficients.
		self._get_coeff()
		
		# Calculate temperature ADC value.
		adc_t = self._data[5] << 16 | self._data[4] << 8 | self._data[3]

		# Calculate temperature coefficient values.
		T1 = self._coeff[0] / 2**-8.0
		T2 = self._coeff[1] / 2**30.0
		T3 = self._coeff[2] / 2**48.0
		
		# Calculate temperature value.
		pd1 = adc_t - T1
		pd2 = pd1 * T2

		temperature: float = pd2 + (pd1 * pd1) * T3

		# Store temperature.
		self._temperature = temperature

		# Return temperature.
		return temperature

	def temperature(self) -> float:
		"""
		Returns:
			`temperature`: BMP390 Temperature value.
		"""
		return self._temperature

	def _calc_pressure(self) -> float:
		"""
		Calculates the pressure value from the sensor data and
		stores the value in the :class:`BMP390_Sensor` object.

		Returns:
			`pressure`: Pressure value.
		"""
		# Get the raw ADC data.
		self._get_data()
		# Get required coefficients.
		self._get_coeff()
		
		# Calculate temperature ADC value.
		adc_p = self._data[2] << 16 | self._data[1] << 8 | self._data[0]

		# Calculate temperature coefficient values.
		P1 = (self._coeff[3] - 2**14.0) / 2**20.0
		P2 = (self._coeff[4] - 2**14.0) / 2**29.0
		P3 = self._coeff[5] / 2**32.0
		P4 = self._coeff[6] / 2**37.0
		P5 = self._coeff[7] / 2**-3.0
		P6 = self._coeff[8] / 2**6.0
		P7 = self._coeff[9] / 2**8.0
		P8 = self._coeff[10] / 2**15.0
		P9 = self._coeff[11] / 2**48.0
		P10 = self._coeff[12] / 2**48.0
		P11 = self._coeff[13] / 2**65.0
		
		# Get temperature value.
		temperature = self._calc_temperature()

		# Calculate temperature value.
		pd1 = P6 * temperature
		pd2 = P7 * temperature**2.0
		pd3 = P8 * temperature**3.0
		po1 = P5 +  pd1 + pd2 + pd3

		pd1 = P2 * temperature
		pd2 = P3 * temperature**2.0
		pd3 = P4 * temperature**3.0
		po2 = adc_p * (P1 +  pd1 + pd2 + pd3)

		pd1 = adc_p**2.0
		pd2 = P9 + P10 * temperature
		pd3 = pd1 * pd2
		pd4 = pd3 + P11 * adc_p**3.0

		pressure: float = po1 + po2 + pd4 / 100

		# Store pressure.
		self._pressure = pressure

		# Return temperature.
		return pressure

	def pressure(self) -> float:
		"""
		Returns:
			`pressure`: BMP390 Pressure value.
		"""
		return self._pressure
	
	def _set_base_pressure(self, pressure: float = None) -> float:
		"""
		Sets the base pressure based on the input.
		
		Arguments:
			`pressure`: Optional float value to which pressure is to be set to.
		
		If no `pressure` parameter is provided, then the pressure value of the
		sensor is calculated and stored as the new `base_pressure`.
		
		Else the provided value is stored as the `base_pressure`.

		Returns:
			`base_pressure`: The base pressure value stored.
		"""
		if pressure is not None:
			self._base_pressure = pressure
		else:
			self._base_pressure = self._calc_pressure()

		return self._base_pressure


	def base_pressure(self) -> float:
		"""
		Returns:
			`base_pressure`: BMP390 Base Pressure value.
		"""
		return self._base_pressure
	

	def _calc_altitude(self) -> float:
		"""
		Calculates the altitude value from the sensor's pressure and temperature data
		and stores the value in the :class:`BMP390_Sensor` object.

		Returns:
			`altitude`: Altitude value.
		"""
		# Read pressure value.
		pressure: float = self._calc_pressure()
		# Read base pressure value.
		base_pressure: float = self._base_pressure
		
		# Calculate altitude.
		altitude: float = 44307.7 * (1 - (pressure / base_pressure)**0.190284)

		# Store altitude.
		self._altitude = altitude

		# Return altitude
		return altitude


	def altitude(self) -> float:
		"""
		Returns:
			`altitude`: BMP390 Altitude value.
		"""
		return self._altitude

	
	def read_values(self) -> List[float]:
		"""
		Calculates the pressure, temperature and altitude from the sensor data
		and stores the value in the :class:`BMP390_Sensor` object.

		Returns:
			`[temperature, pressure, altitude]`: List containing the temperature,
			  pressure and altitude values.
		"""
		# Calculate sensor values.
		self._calc_altitude()

		# Return calculated values.
		return self.temperature(), self.pressure(), self.altitude()


###################

if __name__ == "__main__":
	bus = SMBus(1)
	bus.write_byte_data(0x77,0x1B,0x13)

	while bus.read_byte_data(0x77,0x03) & 0x60 != 0x60:
		time.sleep(0.002)

	data = bus.read_i2c_block_data(0x77,0x04,6)

	adc_p = data[2] << 16 | data[1] << 8 | data[0]
	adc_t = data[5] << 16 | data[4] << 8 | data[3]

	coeff = bus.read_i2c_block_data(0x77,0x31,21)
	#print (coeff)
	coeff = bytes(coeff)
	#print (coeff)
	coeff = struct.unpack("<HHbhhbbHHbbhbb", coeff)

	#print (coeff)

	T1 = coeff[0] / 2**-8.0
	T2 = coeff[1] / 2**30.0
	T3 = coeff[2] / 2**48.0

	P1 = (coeff[3] - 2**14.0) / 2**20.0
	P2 = (coeff[4] - 2**14.0) / 2**29.0
	P3 = coeff[5] / 2**32.0
	P4 = coeff[6] / 2**37.0
	P5 = coeff[7] / 2**-3.0
	P6 = coeff[8] / 2**6.0
	P7 = coeff[9] / 2**8.0
	P8 = coeff[10] / 2**15.0
	P9 = coeff[11] / 2**48.0
	P10 = coeff[12] / 2**48.0
	P11 = coeff[13] / 2**65.0

	pd1 = adc_t - T1
	pd2 = pd1 * T2

	temperature = pd2 + (pd1 * pd1) * T3

	pd1 = P6 * temperature
	pd2 = P7 * temperature**2.0
	pd3 = P8 * temperature**3.0
	po1 = P5 +  pd1 + pd2 + pd3

	pd1 = P2 * temperature
	pd2 = P3 * temperature**2.0
	pd3 = P4 * temperature**3.0
	po2 = adc_p * (P1 +  pd1 + pd2 + pd3)

	pd1 = adc_p**2.0
	pd2 = P9 + P10 * temperature
	pd3 = pd1 * pd2
	pd4 = pd3 + P11 * adc_p**3.0

	pressure = po1 + po2 + pd4
	pressure = pressure / 100

	sea_level_pressure = 935.92 #1013.25
	altitude = 44307.7*(1-(pressure/sea_level_pressure)**0.190284)

	print (temperature)
	print (pressure)
	print (altitude)
