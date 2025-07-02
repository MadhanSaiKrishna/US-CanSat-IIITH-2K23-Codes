# this is the main file for the flight software

"""
OBJECTIVES:
^^^^^^^^^^^
1. Maintain count of transmitted packets despite processor resets [X]
2. Maintain mission time despite processor resets [X]
3. Set CANSAT time to UTC [X]
4. On board telemetry data storage [X]
5. functions to calculate the altitude from pressure [O] -- check the function find_altitude()
6. simulation mode [X]
7. Parse function sent by the ground station [X]


Serial io
--------------
7. Send data to the ground station []
8. Get data from the ground station []
"""

# import software libraries
import csv
import time
from datetime import datetime, timedelta, timezone
# import FSW Data Module
import FSW_Data as Data
# import electronics libraries
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress # XBee
import AHT21B	# Temperature
# import BMP390 # Altitude, Pressure, Temperature
from BMP390 import BMP390_Sensor
import MPU6050	# Aceeleration, Gyroscope, Temperature
import MS4525DO	# Air Speed
from FSW_Sensors import Sensors

# global constants
gl_TEAM_ID = 2085
gl_altitude_calibration = (-1, -1) # a tuple containing the calibration altitude and correspoding pressure value
gnd_station_cmd: str = None
gnd_station_cmd_time: datetime = None
gnd_station_prev_cmd_time: datetime = None

# XBee Settings.
# Ground Station Constants
GROUND_STATION_64BIT_ADDRESS_STRING = "0013A200410908BE"
GROUND_STATION_XBEE_64BIT_ADDRESS = XBee64BitAddress.from_hex_string(GROUND_STATION_64BIT_ADDRESS_STRING)

# Cansat Settings
CANSAT_PORT = "COM4" # Update based on the COM port the XBee is connected to.
CANSAT_BAUD_RATE = 9600
PANID = b"\x20\x85" # HEX 2085

# Instantiate a local XBee object for CANSAT.
cansat = XBeeDevice(CANSAT_PORT, CANSAT_BAUD_RATE)
# Open CANSAT connection.
cansat.open()
# Set the PAN ID and destination address of the device.
cansat.set_pan_id(bytearray(PANID))
cansat.set_dest_address(GROUND_STATION_XBEE_64BIT_ADDRESS)

# Instantiate a remote XBee object for Ground Station.
gnd_station = RemoteXBeeDevice(cansat, GROUND_STATION_XBEE_64BIT_ADDRESS)

# global variables
gl_packets_sent = 0
gl_mode = "Flight"
gl_state = "NA"
gl_telemtry_status = "OFF"
gl_previous_command = None
gl_beacon_status = "OFF"
gl_prev_tel_time = None
gl_telemetry_time_period = 1  # in seconds
gl_simp_pressure = 101325

gl_mission_time = None
gl_mission_init_time = None
gl_system_init_time = None

# Sensors
# BMP390 = BMP390_Sensor()
sensors = Sensors()


def data_receive_callback(xbee_message):
	"""Function to process the received message."""
	global gnd_station_cmd, gnd_station_cmd_time, gl_telemtry_status

	# Read remote device address and received message
	address = xbee_message.remote_device.get_64bit_addr()
	# If remote device address matches the
	# if address == GROUND_STATION_64BIT_ADDRESS_STRING:
	gnd_station_cmd = xbee_message.data.decode("utf8")
	gnd_station_cmd_time = datetime.now()
	# print("Received data from {}: {}".format(address, message))
	print(gnd_station_cmd)

	pass


def get_sensor_data():
	# get data from the sensors
	# and convert to the necessary format

	global gl_TEAM_ID, gl_mission_time, gl_packets_sent, gl_mode, gl_state, gl_previous_command

	# telemetry format
	# <TEAM_ID>, <MISSION_TIME>, <PACKET_COUNT>, <MODE>, <STATE>, 
	# <ALTITUDE>, <AIR_SPEED>, <HS_DEPLOYED>, <PC_DEPLOYED>, 
	# <TEMPERATURE>, <PRESSURE>, <VOLTAGE>, <GPS_TIME>, <GPS_ALTITUDE>, 
	# <GPS_LATITUDE>, <GPS_LONGITUDE>, <GPS_SATS>, <TILT_X>, <TILT_Y>, 
	# <ROT_Z>, <CMD_ECHO>

	# Read sensor data

	data = {}
	# data[Data.attribute_idx["altitude"]] = BMP390.readAltitude()
	data[Data.attribute_idx["altitude"]] = sensors.altitude
	# data[Data.attribute_idx["air_speed"]] = MS4525DO.readAirSpeed()
	data[Data.attribute_idx["air_speed"]] = sensors.air_speed
	# HS_deployed
	# PC_deployed
	# data[Data.attribute_idx["temperature"]] = AHT21B.readTemperature()
	data[Data.attribute_idx["temperature"]] = sensors.temperature
	# data[Data.attribute_idx["pressure"]] = BMP390.readPressure()
	data[Data.attribute_idx["pressure"]] = sensors.pressure
	data[Data.attribute_idx["voltage"]] = sensors.voltage
	data[Data.attribute_idx["GPS_time"]] = sensors.voltage
	data[Data.attribute_idx["GPS_altitude"]] = sensors.voltage
	data[Data.attribute_idx["GPS_latitude"]] = sensors.voltage
	data[Data.attribute_idx["GPS_longitude"]] = sensors.voltage
	data[Data.attribute_idx["GPS_sats"]] = sensors.voltage
	# data[Data.attribute_idx["tiltX"]] = MPU6050.readGyroX()
	# data[Data.attribute_idx["tiltY"]] = MPU6050.readGyroY()
	data[Data.attribute_idx["tiltX"]] = sensors.tilt_X
	data[Data.attribute_idx["tiltY"]] = sensors.tilt_Y
	data[Data.attribute_idx["rotZ"]] = sensors.rotation_Z

	# telemetry = "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}".format(
	# 	gl_TEAM_ID,
	# 	gl_mission_time,
	# 	gl_packets_sent,
	# 	gl_mode,
	# 	gl_state,
	# 	# altitude,
	# 	# air_speed,
	# 	# HS,
	# 	# PC,
	# 	# temperature,
	# 	# pressure,
	# 	# voltage,
	# 	# gps_time,
	# 	# gps_altitude,
	# 	# gps_latitude,
	# 	# gps_longitude,
	# 	# gps_sats,
	# 	# tilt_x,
	# 	# tilt_y,
	# 	# rot_z,
	# 	gl_previous_command
	# )

	return data


def onboard_telemetry_storage(parsed_data):
	# store the data in the onboard memory
	# this function needs to be completed
	with open("Onboard_storage_{}.csv".format(gl_TEAM_ID), "a", newline="") as f:
		writer = csv.writer(f)
		writer.writerow(parsed_data)
	return 0


def send_telemetry(parsed_data):
	# send data to the ground station
	# this function needs to be completed
	cansat.send_data(gnd_station, parsed_data)
	global gl_packets_sent
	onboard_telemetry_storage(parsed_data)
	gl_packets_sent += 1
	pass


def save_through_reset():
	# this function will save the data through processor resets
	"""
	Data that needs to be saved through processor resets:
	1. Mission time
	2. Altitude calibration
	3. Count of packets transmitted
	"""
	with open("Save_reset_{}.csv".format(gl_TEAM_ID), "w", newline="") as f:
		writer = csv.writer(f)
		writer.writerow([gl_altitude_calibration, gl_packets_sent, gl_mission_time])
	return 0


def load_values_from_save_reset():
	# this function will load the data from the save reset file
	# and set the values of the global variables
	global gl_altitude_calibration, gl_packets_sent, gl_mission_time
	with open("Save_reset_{}.csv".format(gl_TEAM_ID), "r", newline="") as f:
		reader = csv.reader(f)
		for row in reader:
			gl_altitude_calibration = row[0]
			gl_packets_sent = row[1]
			gl_mission_time = row[2]
	return 0


def get_GPS_time(parsed_data):
	# this function will get the GPS time
	GPS_time = parsed_data[Data.attribute_idx["GPS_time"]]
	return GPS_time


def current_mission_time():
	# this function will return the current mission time
	global gl_system_init_time, gl_mission_init_time, gl_mission_time
	current_time = datetime.now(timezone.utc)
	current_time = current_time.replace(tzinfo=None)
	gl_system_init_time = gl_system_init_time.replace(tzinfo=None)
	gl_mission_init_time = gl_mission_init_time.replace(tzinfo=None)

	mission_duration = current_time - gl_system_init_time
	gl_mission_time = gl_mission_init_time + mission_duration
	return gl_mission_time


def set_CANSAT_time(UTC_time=None):
	# this function will set the CANSAT time to UTC
	if type(UTC_time) == str:
		UTC_time = datetime.strptime(UTC_time, "%H:%M:%S")

	print(UTC_time)

	global gl_mission_time, gl_mission_init_time, gl_system_init_time
	gl_system_init_time = datetime.now(timezone.utc)
	if UTC_time == None:
		UTC_time = get_GPS_time()

	gl_mission_time = UTC_time
	gl_mission_init_time = UTC_time
	return 0


def calibrate_altitude(parsed_sensor_data):
	# this function will set the altitude calibration
	global gl_altitude_calibration
	gl_altitude_calibration = (0, parsed_sensor_data[Data.attribute_idx["Pressure"]])
	return 0


def find_altitude(parsed_sensor_data):
	# this function will find the altitude from the pressure
	global gl_altitude_calibration
	pressure = parsed_sensor_data[Data.attribute_idx["Pressure"]]

	#####################################################################
	# this is a dummy function to simulate the altitude calculation
	altitude = 44330 * (1 - ((pressure / gl_altitude_calibration[1]) ** (1 / 5.255)))
	#####################################################################
	return altitude


def sensor_data_to_telemetry_format(parsed_sensor_data):
	# this function will convert the sensor data to the telemetry format
	data = {}
	for idx in range(len(Data.attribute_idx)):
		data[idx] = parsed_sensor_data[idx]

	data[Data.attribute_idx["teamID"]] = gl_TEAM_ID
	data[Data.attribute_idx["mission_time"]] = current_mission_time()
	data[Data.attribute_idx["packet_count"]] = gl_packets_sent
	data[Data.attribute_idx["mode"]] = gl_mode
	data[Data.attribute_idx["state"]] = "NA"
	data[Data.attribute_idx["altitude"]] = find_altitude(parsed_sensor_data)
	data[Data.attribute_idx["command_echo"]] = gl_previous_command

	datapt = Data.Data(data)
	parsed_data = datapt.get_parsed_data()
	return datapt


def parse_command(command):
	"""
	- This function parses the command sent by the ground station
	- It returns the command number and the arguments
	- The command number is used to call the appropriate function
	"""
	command = str(command).split(",")
	command_number = command[2]
	arguments = command[3:]
	return command_number, arguments


def call_CANSAT_ops(command_number, arguments, parsed_sensor_data):
	# this function will call the appropriate function
	global gl_telemtry_status, gl_previous_command, gl_beacon_status, gl_mode, gl_simp_pressure
	# call the appropriate function
	if command_number == "CX":
		if arguments[0] == "ON":
			gl_telemtry_status = "ON"
		elif arguments[0] == "OFF":
			gl_telemtry_status = "OFF"
		else:
			print("Invalid argument for CX command")
		gl_previous_command = "CX{}".format(arguments[0])

	elif command_number == "ST":
		if arguments[0] == "GPS":
			set_CANSAT_time()
		else:
			set_CANSAT_time(arguments[0])
		gl_previous_command = "ST{}".format(arguments[0])

	elif command_number == "CAL":
		calibrate_altitude(parsed_sensor_data)
		gl_previous_command = "CAL"

	elif command_number == "BCN":
		if arguments[0] == "ON":
			gl_beacon_status = "ON"
		elif arguments[0] == "OFF":
			gl_beacon_status = "OFF"
		else:
			print("Invalid argument for BCN command")
		gl_previous_command = "BCN{}".format(arguments[0])

	elif command_number == "SIM":
		if arguments[0] == "ENABLE":
			gl_mode = "SIM-1"
		elif arguments[0] == "DISABLE":
			gl_mode = "Flight"
		elif arguments[0] == "ACTIVATE":
			if gl_mode == "SIM-1":
				gl_mode = "SIM"
			else:
				print("Enable simulation mode before using this command")
			gl_previous_command = "SIM{}".format(arguments[0])

		else:
			print("Invalid argument for SIM command")

	elif command_number == "SIMP":
		if gl_mode == "SIM":
			parsed_sensor_data[Data.attribute_idx["Pressure"]] = arguments[0]
			gl_simp_pressure = arguments[0]
		gl_previous_command = "SIMP{}".format(arguments[0])

	else:
		print("Invalid command")

	return 0


if __name__ == "__main__":
	# while input() != "START":
	# 	continue
	# this is the main function

	start_time = datetime.now()

	# setting callback function whenever data is received from ground station
	cansat.add_data_received_callback(data_receive_callback)

	while True:  # this is the loop of the flight software
		# get data from the sensors
		parsed_sensor_data = get_sensor_data()
		parsed_data = sensor_data_to_telemetry_format(parsed_sensor_data)
		if gl_mode == "SIM":
			parsed_sensor_data[Data.attribute_idx["Pressure"]] = gl_simp_pressure

		# parsed_data = "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}".format(
		# 	gl_TEAM_ID,
		# 	datetime.now(),
		# 	gl_packets_sent,
		# 	'S',
		# 	'TESTING',
		# 	0,
		# 	0,
		# 	'N',
		# 	'N',
		# 	32.1,
		# 	1.1,
		# 	3.3,
		# 	datetime.now(),
		# 	23456.7,
		# 	1.0000,
		# 	2.0000,
		# 	24,
		# 	-1.23,
		# 	1.23,
		# 	3.0
		# )


		# if the command exists and previous command time and current command time are different
		if (gnd_station_cmd != None and gnd_station_cmd_time != gnd_station_prev_cmd_time):
			# update past ground station command time
			gnd_station_prev_cmd_time = gnd_station_prev_cmd_time
			# parse the command from the ground station
			command_number, arguments = parse_command(gnd_station_cmd)
			# call the appropriate function
			call_CANSAT_ops(command_number, arguments, parsed_sensor_data)

		cur_time = current_mission_time()
		# cur_time = datetime.now()
		# parsed_data = "{},{},{}".format(gl_TEAM_ID,cur_time,gnd_station_cmd)

		# send data to the ground station
		if gl_telemtry_status == "ON":
			if gl_prev_tel_time == None:
				# time.sleep(5)
				gl_prev_tel_time = cur_time
				send_telemetry(parsed_data)

			if cur_time - gl_prev_tel_time >= timedelta(seconds=gl_telemetry_time_period):
				send_telemetry(parsed_data)
				gl_prev_tel_time = cur_time

		# save the data through processor resets
		save_through_reset()

		if (cur_time - start_time >= timedelta(seconds=15)):
			parsed_data = "{},{},{}".format(gl_TEAM_ID,cur_time,"STOP")
			send_telemetry(parsed_data)
			cansat.close()
			break
