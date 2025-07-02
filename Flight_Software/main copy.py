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

# import libraries
import csv
from datetime import datetime, timedelta, timezone


import Data

# global constants
gl_TEAM_ID = 1000
gl_altitude_calibration = (-1, -1) # a tuple containing the calibration altitude and correspoding pressure value

#global variables
gl_packets_sent = None
gl_mode = "Flight"
gl_state = "NA"
gl_telemtry_status = "OFF"
gl_previous_command = None
gl_beacon_status = "OFF"
gl_prev_tel_time = None
gl_telemetry_time_period = 1 # in seconds
gl_simp_pressure = 101325

gl_mission_time = None
gl_mission_init_time = None
gl_system_init_time = None

def get_sensor_data():
    # get data from the sensors
    # and convert to the necessary format
    pass

def get_command():
    # get the command from the ground station
    # this function needs to be completed
    pass


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
    altitude = (1-((101340 - 101325)**(19.03)))*300/0.65
    print(altitude)
    #####################################################################
    return altitude

def sensor_data_to_telemetry_format(parsed_sensor_data):
    # this function will convert the sensor data to the telemetry format
    data = {}
    for idx in range(len(Data.attribute_idx)):
        data[idx] = parsed_sensor_data[idx]
    
    data[Data.attribute_idx["Mission_time"]] = current_mission_time()
    data[Data.attribute_idx["Altitude"]] = find_altitude(parsed_sensor_data)
    data[Data.attribute_idx["Packet_count"]] = gl_packets_sent
    data[Data.attribute_idx["Team_ID"]] = gl_TEAM_ID
    data[Data.attribute_idx["Mode"]] = gl_mode
    data[Data.attribute_idx["State"]] = "NA"
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
    command = command.split(",")
    command_number = command[2]
    arguments = command[3:]
    return command_number, arguments


def call_CANSAT_ops(command_number, arguments, parsed_sensor_data):
    # this function will call the appropriate function
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

        else:
            print("Invalid argument for SIM command")

    
    elif command_number == "SIMP":
        if gl_mode == "SIM":
            parsed_sensor_data[Data.attribute_idx["Pressure"]] = arguments[0]
            gl_simp_pressure = arguments[0]

    else:
        print("Invalid command")

    return 0


if __name__ == "__main__":
    # this is the main function
    while (1): # this is the loop of the flight software
        # get data from the sensors
        parsed_sensor_data = get_sensor_data()
        parsed_data = sensor_data_to_telemetry_format(parsed_sensor_data)
        if gl_mode == "SIM":
            parsed_sensor_data[Data.attribute_idx["Pressure"]] = gl_simp_pressure

        # get the command from the ground station
        command = get_command()
        command_number, arguments = parse_command(command)

        # call the appropriate function
        call_CANSAT_ops(command_number, arguments, parsed_sensor_data)

        cur_time = current_mission_time()

        # send data to the ground station
        if gl_telemtry_status == "ON":
            if gl_prev_tel_time == None:
                gl_prev_tel_time = cur_time
                send_telemetry(parsed_data)

            if cur_time - gl_prev_tel_time >= timedelta(seconds=gl_telemetry_time_period):
                send_telemetry(parsed_data)
                gl_prev_tel_time = cur_time

        # save the data through processor resets
        save_through_reset()
