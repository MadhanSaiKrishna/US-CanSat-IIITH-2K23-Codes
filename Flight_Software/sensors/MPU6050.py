from smbus2 import SMBus #import SMBus module of I2C
from datetime import datetime, timedelta
from typing import List

# Some MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47
TEMP_OUT     = 0x41
MPU6050_ADDR = 0x69 #0x68


class MPU6050_Sensor():
	"""
	Class for MPU6050 sensor.
	"""

	def __init__(self) -> None:
		"""
		Class constructor. Instantiates the :class:`MPU6050_Sensor`
		with the required properties.
		"""

		# Initialise bus.
		self._bus = SMBus(1)
		# Write to sample rate register.
		self._bus.write_byte_data(MPU6050_ADDR, SMPLRT_DIV, 7)
		# Write to power management register.
		self._bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 1)
		# Write to Configuration register.
		self._bus.write_byte_data(MPU6050_ADDR, CONFIG, 0)
		# Write to Gyro configuration register.
		self._bus.write_byte_data(MPU6050_ADDR, GYRO_CONFIG, 24)
		# Write to interrupt enable register.
		self._bus.write_byte_data(MPU6050_ADDR, INT_ENABLE, 1)

		# Define other values.
		self._temperature: float = None
		self._acc_x: float = None
		self._acc_y: float = None
		self._acc_z: float = None
		self._gyro_x: float = None
		self._gyro_y: float = None
		self._gyro_z: float = None

		return
	
	def _read_raw_data(self, address):
		high = self._bus.read_byte_data(MPU6050_ADDR, address)
		low = self._bus.read_byte_data(MPU6050_ADDR, address + 1)

		# Concatenate higher and lower value
		value = ((high << 8) | low)
		# To get signed value from mpu6050
		if (value > 32768):
			value = value - 65536

		return value

	def _calc_acc_x(self):
		acc_x = self._read_raw_data(ACCEL_XOUT_H)
		#Full scale range +/- 250 degree/C as per sensitivity scale factor
		acceleration = acc_x / 16384.0

		self._acc_x = acceleration
		return acceleration
	
	def acceleration_x(self) -> float:
		"""
		Returns:
			`acceleration`: MPU6050 Acceleration X-Axis value.
		"""
		return self._acc_x

	def _calc_acc_y(self):
		acc_y = self._read_raw_data(ACCEL_YOUT_H)
		#Full scale range +/- 250 degree/C as per sensitivity scale factor
		acceleration = acc_y / 16384.0

		self._acc_y = acceleration
		return acceleration
	
	def acceleration_y(self) -> float:
		"""
		Returns:
			`acceleration`: MPU6050 Acceleration Y-Axis value.
		"""
		return self._acc_y

	def _calc_acc_z(self):
		acc_z = self._read_raw_data(ACCEL_ZOUT_H)
		#Full scale range +/- 250 degree/C as per sensitivity scale factor
		acceleration = acc_z / 16384.0

		self._acc_y = acceleration
		return acceleration
	
	def acceleration_z(self) -> float:
		"""
		Returns:
			`acceleration`: MPU6050 Acceleration Z-Axis value.
		"""
		return self._acc_z

	def _calc_gyro_x(self):
		gyro_x = self._read_raw_data(ACCEL_XOUT_H)
		#Full scale range +/- 250 degree/C as per sensitivity scale factor
		gyro = gyro_x / 131.0

		self._gyro_x = gyro
		return gyro
	
	def gyro_x(self) -> float:
		"""
		Returns:
			`gyro`: MPU6050 Gyro X-Axis value.
		"""
		return self._gyro_x

	def _calc_gyro_y(self):
		gyro_y = self._read_raw_data(ACCEL_YOUT_H)
		#Full scale range +/- 250 degree/C as per sensitivity scale factor
		gyro = gyro_y / 131.0

		self._gyro_y = gyro
		return gyro
	
	def gyro_y(self) -> float:
		"""
		Returns:
			`gyro`: MPU6050 Gyro Y-Axis value.
		"""
		return self._gyro_y

	def _calc_gyro_z(self):
		gyro_z = self._read_raw_data(ACCEL_ZOUT_H)
		#Full scale range +/- 250 degree/C as per sensitivity scale factor
		gyro = gyro_z / 131.0

		self._gyro_y = gyro
		return gyro
	
	def gyro_z(self) -> float:
		"""
		Returns:
			`gyro`: MPU6050 Gyro Z-Axis value.
		"""
		return self._gyro_z

	def _calc_temperature(self):
		temp = self._read_raw_data(ACCEL_ZOUT_H)
		#Full scale range +/- 250 degree/C as per sensitivity scale factor
		T = (temp / 340) + 36.53
		return T
	
	def temperature(self) -> float:
		"""
		Returns:
			`temperature`: MPU6050 Temperature value.
		"""
		return self._temperature
	
	def read_values(self) -> List[float]:
		"""
		Calculates the channel 0 and channel 1 voltages from the sensor data
		and stores the value in the :class:`ADS1115_Sensor` object.

		Returns:
			`List[float]`: List of length 7 containing the acceleration and 
			 gyro values of all three axes, and the temperature.
		"""
		return [
			self._calc_acc_x(),
			self._calc_acc_y(),
			self._calc_acc_z(),
			self._calc_gyro_x(),
			self._calc_gyro_y(),
			self._calc_gyro_z(),
			self._calc_temperature()
		]


def testModule():
	sensor = MPU6050_Sensor()
	print (" Reading Data of Gyroscope, Accelerometer and Temperature")
	Ax, Ay, Az, Gx, Gy, Gz, T = sensor.read_values()
	print ("Gx=%.2f" %Gx, u'\u00b0'+ "/s", "\tGy=%.2f" %Gy, u'\u00b0'+ "/s", "\tGz=%.2f" %Gz, u'\u00b0'+ "/s", "\tAx=%.2f g" %Ax, "\tAy=%.2f g" %Ay, "\tAz=%.2f g" %Az, "\tTemperature=%.2f" %T)
#	print (f"Ax = {Ax}, Ay = {Ay}, Az = {Az}, Gx = {Gx}, Gy = {Gy}, Gz = {Gz}, T = {T}")


if __name__ == "__main__":
	time = datetime.now()
	while True:
		if (datetime.now() - time) >= timedelta(seconds = 1):
			time = datetime.now()
			testModule()
