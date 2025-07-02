from typing import List, Any
from ADS1115 import ADS1115_Sensor
from AHT21B import AHT21B_Sensor
from BMP390 import BMP390_Sensor
from DS3231 import DS3231_Sensor
from MPU6050 import MPU6050_Sensor
from MS4525DO import MS4525DO_Sensor

# SENSOR STATUS CODES
ADS1115_INIT_FAIL = -1
AHT21B_INIT_FAIL = -2
BMP390_INIT_FAIL = -3
DS3231_INIT_FAIL = -4
MPU6050_INIT_FAIL = -5
MS4525DO_INIT_FAIL = -6

"""
TODO:
- Figure out GPS data []
"""
import serial
import pynmea2
import datetime

def get_gps_data(port="/dev/serial0", baudrate=9600, timeout=0.1):
    ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
    while True:
        newdata = ser.readline()
        if newdata[0:6] == "$GPGGA":
            msg = pynmea2.parse(newdata)
            GPS_time = msg.timestamp
            GPS_altitude = msg.altitude
            GPS_latitude = msg.latitude
            GPS_longitude = msg.longitude
            num_sats = msg.num_sats
            return GPS_time, GPS_altitude, GPS_latitude, GPS_longitude, num_sats


class Sensors:
	"""
	Class for all sensors combined.
	"""

	def __init__(self) -> None:
		"""
		Class constructor. Initialises a :class:`Sensors` object,
		along with the appropriate sensor modules and values.
		"""

		# Sensor modules and individual values.
		## BMP390
		try:
			self._bmp390 = BMP390_Sensor()
		except:
			print("Failed to Initialize BMP390 Sensor.")
			self._bmp390 = None

		self._bmp390_temperature: float = None
		self._bmp390_pressure: float = None
		self._bmp390_altitude: float = None
		
		## ADS1115
		try:
			self._ads1115 = ADS1115_Sensor()
		except:
			print("Failed to Initialize ADS1115 Sensor.")
			self._ads1115 = None
		self._ads1115_channel_0: float = None
		self._ads1115_channel_1: float = None
		self._ads1115_voltage: float = None
		
		## AHT21B
		try:
			self._aht21b = None
			# self._aht21b = AHT21B_Sensor()
		except:
			self._aht21b = None
		self._aht21b_temperature: float = None
		
		## DS3231
		try:
			self._ds3231 = None
			# self._ds3231 = DS3231_Sensor()
		except:
			self._ds3231 = None
		self._ds3231_raw_time: List[int] = None
		self._ds3231_telemetry_time: str = None

		## MPU6050
		# self._mpu6050 = MPU6050_Sensor()
		self._mpu6050_temperature: float = -1.0
		self._mpu6050_acc_x: float = -1
		self._mpu6050_acc_y: float = -1
		self._mpu6050_acc_z: float = -1
		self._mpu6050_gyro_x: float = -1
		self._mpu6050_gyro_y: float = -1
		self._mpu6050_gyro_z: float = -1

		## MS4525DO
		try:
			self._ms4525do = None
			# self._ms4525do = MS4525DO_Sensor()
		except:
			self._ms4525do = None
		self._ms4525do_pressure: float = None
		self._ms4525do_air_speed: float = None
		pass ## Add other sensors

		## NEO-M8N
		self._neo_m8n_time: str = None
		self._neo_m8n_altitude: float = None
		self._neo_m8n_latitude: float = None
		self._neo_m8n_longitude: float = None
		self._neo_m8n_sats: int = None

		# Data values.
		self.altitude: float = 0.0

		self.air_speed: float = 0.0
		if self._ms4525do_air_speed is not None:
			self.air_speed: float = self._ms4525do_air_speed
		
		
		self.temperature: float = 0.0
		if self._aht21b_temperature is not None:
			self.temperature: float = self._aht21b_temperature

		
		self.pressure: float = 101325.0
		if self._bmp390_pressure is not None:
			self.pressure: float = self._bmp390_pressure

		
		self.voltage: float = 0.0
		if self._ads1115_voltage is not None:
			self.voltage: float = self._ads1115_voltage

		
		self.GPS_time: str = datetime.datetime.now().strftime("%H:%M:%S")
		if self._neo_m8n_time is not None:
			self.GPS_time: str = self._neo_m8n_time

		self.GPS_altitude: float = 432.3
		if self._neo_m8n_altitude is not None:
			self.GPS_altitude: float = self._neo_m8n_altitude

		
		self.GPS_latitude: float = 38.1496
		if self._neo_m8n_latitude is not None:
			self.GPS_latitude: float = self._neo_m8n_latitude

		self.GPS_longitude: float = 79.0717
		if self._neo_m8n_longitude is not None:
			self.GPS_longitude: float = self._neo_m8n_longitude


		self.GPS_sats: int = 3
		if self._neo_m8n_sats is not None:
			self.GPS_sats: int = self._neo_m8n_sats

		
		self.tilt_X: float = 0.00
		self.tilt_Y: float = 0.00
		self.rotation_Z: float = 0.0

		self.optional_data: str = None

		self.cam1: str = None
		self.cam2: str = None

		return

	def _update_bmp390_values(self) -> List[float]:
		"""
		Function to update values from BMP390.
		
		Returns:
			`temperature`, `pressure`, `altitude` readings from BMP390.
		"""
		if self._bmp390 is not None:
			self._bmp390_temperature, self._bmp390_pressure, self._bmp390_altitude = self._bmp390.read_values()
		else:
			try:
				self._bmp390 = BMP390_Sensor()
			except:
				print("Failed to Initialize BMP390 Sensor.")
				self._bmp390 = None
			else:
				self._bmp390_temperature, self._bmp390_pressure, self._bmp390_altitude = self._bmp390.read_values()

		return self._bmp390_temperature, self._bmp390_pressure, self._bmp390_altitude

	def callibrate_base_pressure(self, base_pressure: float = None):
		return self._bmp390._set_base_pressure(base_pressure)

	def _update_ads1115_values(self) -> List[float]:
		"""
		Function to update values from ADS1115.
		
		Returns:
			`channel_0_voltage`, `channel_1_voltage` readings from ADS1115.
		"""
		if self._ads1115 is not None:
			self._ads1115_channel_0, self._ads1115_channel_1 = self._ads1115.read_values()
		else:
			try:
				self._ads1115 = ADS1115_Sensor()
			except:
				print("Failed to Initialize ADS1115 Sensor.")
				self._ads1115 = None
			else:
				self._ads1115_channel_0, self._ads1115_channel_1 = self._ads1115.read_values()

		return self._ads1115_channel_0, self._ads1115_channel_1

	def _update_aht21b_values(self) -> List[float]:
		"""
		Function to update temperature from AHT21B.
		
		Returns:
			`temperature` reading from AHT21B.
		"""
		if self._aht21b is not None:
			self._aht21b_temperature = self._aht21b.read_value()
		else:
			try:
				self._aht21b = AHT21B_Sensor()
			except:
				self._aht21b = None
			else:
				self._aht21b_temperature = self._aht21b.read_value()

		return self._aht21b_temperature

	def _update_mpu6050_values(self) -> List[float]:
		"""
		Function to update values from MPU6050.
		
		Returns:
			`temperature` reading from MPU6050.
		"""
		[
			self._mpu6050_temperature,
			self._mpu6050_acc_x,
			self._mpu6050_acc_y,
			self._mpu6050_acc_z,
			self._mpu6050_gyro_x,
			self._mpu6050_gyro_y,
			self._mpu6050_gyro_z
		] = self._mpu6050.read_values()

		return [
			self._mpu6050_temperature,
			self._mpu6050_acc_x,
			self._mpu6050_acc_y,
			self._mpu6050_acc_z,
			self._mpu6050_gyro_x,
			self._mpu6050_gyro_y,
			self._mpu6050_gyro_z
		]

	def _update_ms4525do_values(self) -> List[float]:
		"""
		Function to update values from MS4525DO.
		
		Returns:
			`pressure`, `air_speed` readings from MS4525DO.
		"""
		if self._ms4525do is not None:
			self._ms4525do_pressure, self._ms4525do_air_speed = self._ms4525do.read_values()
		else:
			try:
				self._ms4525do = MS4525DO_Sensor()
			except:
				self._ms4525do = None
			else:
				self._ms4525do_pressure, self._ms4525do_air_speed = self._ms4525do.read_values()

		return self._ms4525do_pressure, self._ms4525do_air_speed
	
	def _update_ds3231_values(self) -> tuple[List[int], str]:
		"""
		Function to update values from DS3231.
		
		Returns:
			`raw_time`, `telemetry_time` readings from DS3231.
		"""
		if self._ds3231 is not None:
			self._ds3231_raw_time, self._ds3231_telemetry_time = self._ds3231.read_values()
		else:
			try:
				self._ds3231 = DS3231_Sensor()
			except:
				self._ds3231 = None
			else:
				self._ds3231_raw_time, self._ds3231_telemetry_time = self._ds3231.read_values()

		return self._ds3231_raw_time, self._ds3231_telemetry_time

	def _calc_voltage(self) -> float:
		if self._ads1115 is not None:
			return self._ads1115_channel_0
			# return self._ads1115_channel_0 + self._ads1115_channel_1
		return 0.0

	def update_sensor_values(self):
		# try:
			self._update_ads1115_values()
			# self._update_aht21b_values()
			self._update_bmp390_values()
			# self._update_ds3231_values()
			# self._update_mpu6050_values()
			# self._update_ms4525do_values()
		# except:
		# 	return False
		# else:
		# 	return True

	def update_values(self, update_raw=False):
		if update_raw:
			self.update_sensor_values()
			# while not self.update_sensor_values():
				# print("Trying to read again.")

		self.altitude: float = 0.0

		self.air_speed: float = 0.0
		if self._ms4525do_air_speed is not None:
			self.air_speed: float = self._ms4525do_air_speed
		
		
		self.temperature: float = 0.0
		if self._aht21b_temperature is not None:
			# self.temperature: float = self._aht21b_temperature
			self.temperature: float = self._bmp390_temperature

		
		self.pressure: float = 101325.0
		if self._bmp390_pressure is not None:
			self.pressure: float = self._bmp390_pressure

		
		self.voltage: float = 0.0
		self._ads1115_voltage = self._calc_voltage()
		if self._ads1115_voltage is not None:
			self.voltage: float = self._ads1115_voltage

		
		self.GPS_time: str = None
		if self._neo_m8n_time is not None:
			self.GPS_time: str = self._neo_m8n_time

		self.GPS_altitude: float = 0.0
		if self._neo_m8n_altitude is not None:
			self.GPS_altitude: float = self._neo_m8n_altitude

		
		self.GPS_latitude: float = 0.0000
		if self._neo_m8n_latitude is not None:
			self.GPS_latitude: float = self._neo_m8n_latitude

		self.GPS_longitude: float = 0.0000
		if self._neo_m8n_longitude is not None:
			self.GPS_longitude: float = self._neo_m8n_longitude


		self.GPS_sats: int = 0
		if self._neo_m8n_sats is not None:
			self.GPS_sats: int = self._neo_m8n_sats


		# self.air_speed = self._ms4525do_air_speed
		# self.altitude = self._bmp390_altitude
		# # self.GPS_altitude
		# # self.GPS_latitude
		# # self.GPS_longitude
		# # self.GPS_sats
		# # self.GPS_time
		# self.optional_data = ""
		# # self.pressure = self._calc_pressure()
		# self.pressure = self._bmp390_pressure
		# self.rotation_Z = self._mpu6050_gyro_z
		# # self.temperature = self._calc_temperature()
		# self.temperature = self._aht21b_temperature
		# self.telemetry_time = self._ds3231_telemetry_time
		# self.tilt_X = self._mpu6050_gyro_x
		# self.tilt_Y = self._mpu6050_gyro_y
		# self.voltage = self._calc_voltage()

		return

	def read_values(self) -> list:
		return [
			self.altitude,
			self.air_speed,
			self.temperature,
			self.pressure,
			self.voltage,
			self.GPS_time,
			self.GPS_altitude,
			self.GPS_latitude,
			self.GPS_longitude,
			self.GPS_sats,
			self.tilt_X,
			self.tilt_Y,
			self.rotation_Z,
			# self.telemetry_time,
			self.optional_data
		]

	def get_values(self, update_raw=False) -> list:
		self.update_values(update_raw)
		return self.read_values()
