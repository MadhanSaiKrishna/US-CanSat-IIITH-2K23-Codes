from datetime import datetime

attribute_idx = {
	"teamID": 0,
	"mission_time": 1,
	"packet_count": 2,
	"mode": 3,
	"state": 4,
	"altitude": 5,
	"air_speed": 6,
	"HS_deployed": 7,
	"PC_deployed": 8,
	"temperature": 9,
	"pressure": 10,
	"voltage": 11,
	"GPS_time": 12,
	"GPS_altitude": 13,
	"GPS_latitude": 14,
	"GPS_longitude": 15,
	"GPS_sats": 16,
	"tiltX": 17,
	"tiltY": 18,
	"rotZ": 19,
	"command_echo": 20,
	"optional_data": 21
}

attribute_datatypes = {
	0: "int",
	1: "dt",
	2: "int",
	3: "str",
	4: "str",
	5: "float",
	6: "float",
	7: "str",
	8: "str",
	9: "float",
	10: "float",
	11: "float",
	12: "dt",
	13: "float",
	14: "float",
	15: "float",
	16: "int",
	17: "float",
	18: "float",
	19: "float",
	20: "str",
	21: "str"
}

class Data:
	def __init__(self, serial_data):
		self.serial_data = serial_data
		self.teamID = self.get_idx(attribute_idx["teamID"])
		self.mission_time = self.get_idx(attribute_idx["mission_time"])
		self.packet_count = self.get_idx(attribute_idx["packet_count"])
		self.mode = self.get_idx(attribute_idx["mode"])
		self.state = self.get_idx(attribute_idx["state"])
		self.altitude = self.get_idx(attribute_idx["altitude"])
		self.air_speed = self.get_idx(attribute_idx["air_speed"])
		self.HS_deployed = self.get_idx(attribute_idx["HS_deployed"])
		self.PC_deployed = self.get_idx(attribute_idx["PC_deployed"])
		self.temperature = self.get_idx(attribute_idx["temperature"])
		self.pressure = self.get_idx(attribute_idx["pressure"])
		self.voltage = self.get_idx(attribute_idx["voltage"])
		self.GPS_time = self.get_idx(attribute_idx["GPS_time"])
		self.GPS_altitude = self.get_idx(attribute_idx["GPS_altitude"])
		self.GPS_latitude = self.get_idx(attribute_idx["GPS_latitude"])
		self.GPS_longitude = self.get_idx(attribute_idx["GPS_longitude"])
		self.GPS_sats = self.get_idx(attribute_idx["GPS_sats"])
		self.tiltX = self.get_idx(attribute_idx["tiltX"])
		self.tiltY = self.get_idx(attribute_idx["tiltY"])
		self.rotZ = self.get_idx(attribute_idx["rotZ"])
		self.command_echo = self.get_idx(attribute_idx["command_echo"])
		self.optional_data = self.get_idx(attribute_idx["optional_data"])
		self.idx_attribute = {
			0: self.teamID,
			1: self.mission_time,
			2: self.packet_count,
			3: self.mode,
			4: self.state,
			5: self.altitude,
			6: self.air_speed,
			7: self.HS_deployed,
			8: self.PC_deployed,
			9: self.temperature,
			10: self.pressure,
			11: self.voltage,
			12: self.GPS_time,
			13: self.GPS_altitude,
			14: self.GPS_latitude,
			15: self.GPS_longitude,
			16: self.GPS_sats,
			17: self.tiltX,
			18: self.tiltY,
			19: self.rotZ,
			20: self.command_echo,
			21: self.optional_data
		}

	
	def get_parsed_data(self):
		self.parsed_data = []
		for idx in range(len(self.idx_attribute)):
			self.parsed_data.append(self.idx_attribute[idx])
		return self.parsed_data

	def convert_to_format(self, data, datatype):
		if datatype == "int":
			data = int(data)
		elif datatype == "float":
			data = float(data)
		elif datatype == "str":
			data = str(data)
		elif datatype == "dt":
			# data = datetime.strptime(data, "%H:%M:%S").time()
			data = str(data)
		return data

	def get_idx(self, idx):
		serial_data = self.serial_data
		data = serial_data.split(",")[idx]
		data = data.strip(" ")
		data = data.strip("'")
		data = self.convert_to_format(data, attribute_datatypes[idx])
		return data


class Sensor_Data:
	def __init__(self, sensor_data):
		self.sensor_data = sensor_data
	   
		self.altitude = self.get_idx(attribute_idx["altitude"])
		self.air_speed = self.get_idx(attribute_idx["air_speed"])
		self.HS_deployed = self.get_idx(attribute_idx["HS_deployed"])
		self.PC_deployed = self.get_idx(attribute_idx["PC_deployed"])
		self.temperature = self.get_idx(attribute_idx["temperature"])
		self.pressure = self.get_idx(attribute_idx["pressure"])
		self.voltage = self.get_idx(attribute_idx["voltage"])
		self.GPS_time = self.get_idx(attribute_idx["GPS_time"])
		self.GPS_altitude = self.get_idx(attribute_idx["GPS_altitude"])
		self.GPS_latitude = self.get_idx(attribute_idx["GPS_latitude"])
		self.GPS_longitude = self.get_idx(attribute_idx["GPS_longitude"])
		self.GPS_sats = self.get_idx(attribute_idx["GPS_sats"])
		self.tiltX = self.get_idx(attribute_idx["tiltX"])
		self.tiltY = self.get_idx(attribute_idx["tiltY"])
		self.rotZ = self.get_idx(attribute_idx["rotZ"])
		self.optional_data = self.get_idx(attribute_idx["optional_data"])
		self.idx_attribute = {
			5: self.altitude,
			6: self.air_speed,
			7: self.HS_deployed,
			8: self.PC_deployed,
			9: self.temperature,
			10: self.pressure,
			11: self.voltage,
			12: self.GPS_time,
			13: self.GPS_altitude,
			14: self.GPS_latitude,
			15: self.GPS_longitude,
			16: self.GPS_sats,
			17: self.tiltX,
			18: self.tiltY,
			19: self.rotZ,
			21: self.optional_data
		}
	
	def get_parsed_data(self):
		self.parsed_data = {}
		for idx in range(len(self.idx_attribute)):
			self.parsed_data[idx] = self.idx_attribute[idx]
		return self.parsed_data

	def convert_to_format(self, data, datatype):
		if datatype == "int":
			data = int(data)
		elif datatype == "float":
			data = float(data)
		elif datatype == "str":
			data = str(data)
		elif datatype == "dt":
			# data = datetime.strptime(data, "%H:%M:%S").time()
			data = str(data)
		return data

	def get_idx(self, idx):
		serial_data = self.serial_data
		data = serial_data.split(",")[idx]
		data = data.strip(" ")
		data = data.strip("'")
		data = self.convert_to_format(data, attribute_datatypes[idx])
		return data
