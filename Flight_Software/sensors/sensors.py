from datetime import datetime, timedelta
import AHT21B	# Temperature
import MPU6050	# Aceeleration, Gyroscope, Temperature
import MS4525DO	# Air Speed


def runner():
	curr_time = datetime.now()
	while True:
		if datetime.now() - curr_time >= timedelta(seconds=1):
			curr_time = datetime.now()
#			print(f"AHT21B Temperature: {AHT21B.readTemperature()}")
#			print(f"MPU6050 Temperature: {MPU6050.readTemperature()}")
#			print(f"MPU6050 X-Axis Acceleration: {MPU6050.readAccX()}")
#			print(f"MPU6050 Y-Axis Acceleration: {MPU6050.readAccY()}")
#			print(f"MPU6050 Z-Axis Acceleration: {MPU6050.readAccZ()}")
#			print(f"MPU6050 X-Axis Gyroscope: {MPU6050.readGyroX()}")
#			print(f"MPU6050 Y-Axis Gyroscope: {MPU6050.readGyroY()}")
#			print(f"MPU6050 Z-Axis Gyroscope: {MPU6050.readGyroZ()}")
			print(f"MS4525DO Air Speed: {MS4525DO.readAirSpeed()}")


if __name__ == "__main__":
	runner()
