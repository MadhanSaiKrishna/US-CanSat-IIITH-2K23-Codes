# This is the main file for the flight software

"""
OBJECTIVES:
^^^^^^^^^^^
1. Maintain count of transmitted packets despite processor resets [X]
2. Maintain mission time despite processor resets [X]
3. Set CANSAT time to UTC [X]
4. On board telemetry data storage [X]
5. functions to calculate the altitude from pressure [O] -- check the function calculate_altitude_from_pressure()
6. simulation mode [X]
7. Parse function sent by the ground station [X]

8. Add dual processor functionality []
9. Add Camera functionality []

Serial io
--------------
7. Send data to the ground station []
8. Get data from the ground station []

9. Create an interrupt for the ground station command []
10. Create time interrupt to send telemetry data []
"""

"""
TODO:
1. Get sensor data only once in 0.1 seconds [X]
2. Modify the receive callback function [X]
3. Complete get_GPS_time() function [X]
4. Check current_mission_time() function [X]
5. Load values from save reset - loop [X]
6. In simulation mode, the pressure value will be overwritten by the sensor pressure value [X]
7. Check the ST command [X]
8. Copy code for 2nd processor [] -------------------------------

############## Huge pending tasks #################
1. parachute deployment - communicate to electronics, mechanism [X] -----------------------
2. heatshield deployment - communicate to electronics, mechanism [X]
3. beacon on off - communicate to electronics [X]
4. camera - just do the FSW_sensors file [X]
5. change the state of the cansat - NA, ascend, descend, landing, recovery [X]
###################################################
"""


import sys
import csv
from datetime import datetime, timedelta, timezone
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress  # XBee

############ UNCOMMENT LATER ###################
# from picamera2.encoders import H264Encoder
# from picamera2 import Picamera2
################################################

# import sensor libraries
sys.path.insert(0, './sensors')
from FSW_Sensors import Sensors

############### ONLY IN P1 #####################
from sender import send_message
###############################################

#################### UNCOMMENT LATER ####################
from PC_Servo import parachute_servo
from HS_deploy_servo import HS_deploy_servo # P1 - deploys HS; P2 - releases HS
from Beacon import beacon_on, beacon_off
##########################################################

sys.path.insert(0, '../Ground_Station')
import Data


########################### Global constants ########################
gl_exit = False
gl_TEAM_ID = 2085
gl_packets_sent = 1 # this is initialised to 1 becuase the we send then increment
gl_mode = "Flight" # its either "SIM" or "Flight" or "SIM-1" (simulation enabled but not activated)
gl_state = "NA" # NA, Ascend, Descent (Heatshield), Landing (Parachute), Recovery
gl_telemtry_status = "ON"
gl_previous_command = "CXON"
gl_beacon_status = "OFF"
gl_prev_tel_time = None
gl_telemetry_time_period = 1  # in seconds
gl_simp_pressure = 101325

gl_prev_sampling_time = datetime.now(timezone.utc).replace(tzinfo=None)
gl_sampling_time_period = 0.1
gl_parachute_servo_angle = 90
gl_HS_deploy_servo_angle = 150

gl_mission_time = 0
gl_mission_init_time = datetime.now(timezone.utc).replace(tzinfo=None)
gl_system_init_time = datetime.now(timezone.utc).replace(tzinfo=None)

gl_HS_deployed = False
gl_PC_deployed = False
gl_max_altitude = 0
gl_send_error = "All OK"

#ADDED FOR THE SECONDARY PROCESSOR 
gl_running_processor = "Primary"
gl_processor_name = "Primary"

# a tuple containing the calibration altitude and correspoding pressure value
gl_zero_altitude_pressure = 101325
gl_gnd_station_cmd: str = None
gl_gnd_station_cmd_time: datetime = None
gnd_station_prev_cmd_time: datetime = None



########################## XBee Settings and Send Telemetry ############################
GROUND_STATION_64BIT_ADDRESS_STRING = "0013A200410908BE"
GROUND_STATION_XBEE_64BIT_ADDRESS = XBee64BitAddress.from_hex_string(GROUND_STATION_64BIT_ADDRESS_STRING)

# Cansat Settings
# CANSAT_PORT = "/dev/ttyS0"  # Update based on the COM port the XBee is connected to.
CANSAT_PORT = "/dev/serial0"  # Update based on the COM port the XBee is connected to.
CANSAT_BAUD_RATE = 9600
PANID = b"\x20\x85"  # HEX 2085


################################## UNCOMMENT LATER ###################################
######################### Picamera Settings ############################
# picam2 = Picamera2()
# video_config = picam2.create_video_configuration()
# picam2.configure(video_config)
# encoder = H264Encoder(bitrate=10000000)
# output = 'test2.h264'
######################################################################################


# Instantiate a local XBee object for CANSAT.
gl_cansat = XBeeDevice(CANSAT_PORT, CANSAT_BAUD_RATE)
gnd_station = RemoteXBeeDevice(gl_cansat, GROUND_STATION_XBEE_64BIT_ADDRESS)

def data_receive_callback(xbee_message):
    """
    Function to process the received message (commands).
    """
    global gl_gnd_station_cmd, gl_gnd_station_cmd_time

    # Read remote device address and received message
    address = xbee_message.remote_device.get_64bit_addr()
    gl_gnd_station_cmd = xbee_message.data.decode("utf8")
    gl_gnd_station_cmd_time = datetime.now()
    print(gl_gnd_station_cmd)


def onboard_telemetry_storage(parsed_data):
    """
    Function to store the data in the onboard memory.
    """
    with open(f"Onboard_storage_{gl_TEAM_ID}.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(parsed_data)
    return 0


def send_telemetry(parsed_data):
    """"
    Function to send telemetry data to the ground station
    """

    global gl_packets_sent
    data_to_send = list(parsed_data.values())
    onboard_telemetry_storage(data_to_send)
    data_to_send = ",".join(data_to_send)
    data_to_send += ",END_TELEMETRY"

    #################### UNCOMMENT LATER ####################
    gl_cansat.send_data(gnd_station, data_to_send)
    #######################################################
    gl_packets_sent += 1
    print(data_to_send)
    return 0

#################### ONLY IN P1 #######################
def send_to_P2(parsed_data):
    """
    Function to send data to the secondary processor
    """
    global gl_running_processor
    data_to_send = list(parsed_data.values())
    data_to_send = ",".join(data_to_send)
    data_to_send += ",END_TELEMETRY"
    send_message(data_to_send)
    return 0
######################################################

################################# Sensor Data ############################
def get_sensor_data():
    """
    Fucntion to get data from the sensors and convert to the necessary format
    """

    global gl_TEAM_ID, gl_mission_time, gl_packets_sent, gl_mode, gl_state, gl_previous_command

    # Store sensor data
    pressure = sensors.pressure
    data = {}
    data["altitude"] = calculate_altitude_from_pressure(pressure)
    data["air_speed"] = sensors.air_speed
    data["temperature"] = sensors.temperature
    data["pressure"] = sensors.pressure
    data["voltage"] = sensors.voltage
    
    data["GPS_time"] = sensors.GPS_time
    data["GPS_altitude"] = sensors.GPS_altitude
    ########################### SCAMMING THE GPS ALTITUDE ############################
    # import random
    # # data["GPS_time"] = (datetime.now() - timedelta(seconds=15)).strftime("%H:%M:%S")
    # data["GPS_time"] = (datetime.now()).strftime("%H:%M:%S")
    # data["GPS_altitude"] = sensors.GPS_latitude + calculate_altitude_from_pressure(sensors.pressure) + 2*random.random() - 1
    ###################################################################################
    data["GPS_latitude"] = sensors.GPS_latitude
    data["GPS_longitude"] = sensors.GPS_longitude
    

    data["GPS_sats"] = sensors.GPS_sats
    ########################### SCAMMING THE GPS SATELLITES ############################
    # data["GPS_sats"] = sensors.GPS_sats + random.randint(0, 1)
    ###################################################################################
    
    data["tiltX"] = sensors.tilt_X
    data["tiltY"] = sensors.tilt_Y
    data["rotZ"] = sensors.rotation_Z
    data["cam1"] = sensors.cam1
    data["cam2"] = sensors.cam2
    return data

    # NOTE: the primary processor (P1 - this) will get the camera data "cam1" : 31


def current_mission_time():
    """
    This function will return the current mission time.
    """
    global gl_system_init_time, gl_mission_init_time, gl_mission_time    
    current_time = datetime.now(timezone.utc).replace(tzinfo=None)
    mission_duration = current_time - gl_system_init_time
    gl_mission_time = gl_mission_init_time + mission_duration
    return gl_mission_time


def calculate_altitude_from_pressure(pressure):
    """
    This function calculates find the altitude from the pressure
    """
    
    global gl_zero_altitude_pressure
    P = pressure

    h_b = 0 # Should be 625 (height above sea level actually)
    T_b = 298.15
    P_b = gl_zero_altitude_pressure
    L_b = -0.0065
    R = 8.31432
    g = 9.81
    M = 0.0289644
    altitude =  h_b + 0.0003*T_b/L_b * ((P/P_b)**(-R*L_b/(g*M)) - 1)
    return altitude


def sensor_data_to_telemetry_format(parsed_sensor_data): # parsed sensor data is a dictionary
    """
    This function will convert the sensor data to the telemetry format
    """

    data = {}
    data["teamID"] = gl_TEAM_ID
    data["mission_time"] = current_mission_time().strftime("%H:%M:%S")
    data["packet_count"] = gl_packets_sent

    if gl_mode == "SIM":
        data["mode"] = "S"
    else:
        data["mode"] = "F"

    data["state"] = gl_state
    data["altitude"] = calculate_altitude_from_pressure(parsed_sensor_data["pressure"])
    data["air_speed"] = parsed_sensor_data["air_speed"]
    
    if gl_HS_deployed:
        data["HS_deployed"] = "P"
    else:
        data["HS_deployed"] = "N"

    if gl_PC_deployed:
        data["PC_deployed"] = "C"
    else:
        data["PC_deployed"] = "N"

    data["temperature"] = parsed_sensor_data["temperature"]
    data["pressure"] = parsed_sensor_data["pressure"]
    data["voltage"] = parsed_sensor_data["voltage"]
    data["GPS_time"] = parsed_sensor_data["GPS_time"]
    data["GPS_altitude"] = parsed_sensor_data["GPS_altitude"]
    data["GPS_latitude"] = parsed_sensor_data["GPS_latitude"]
    data["GPS_longitude"] = parsed_sensor_data["GPS_longitude"]
    data["GPS_sats"] = parsed_sensor_data["GPS_sats"]
    data["tiltX"] = parsed_sensor_data["tiltX"]
    data["tiltY"] = parsed_sensor_data["tiltY"]
    data["rotZ"] = parsed_sensor_data["rotZ"]
    data["command_echo"] = gl_previous_command
    data["optional_data"] = gl_send_error
    data["cam1"] = parsed_sensor_data["cam1"]
    data["cam2"] = parsed_sensor_data["cam2"]

    data_list = list(data.values())
    datapt = Data.Data(data_list)
    parsed_data = datapt.get_parsed_data()

    for i in parsed_data.keys():
        parsed_data[i] = str(parsed_data[i])
    return parsed_data


###################### PARSING COMMANDS RECEIVED FROM GCS ###########################
def parse_command(command):
    """
    - This function parses the command sent by the ground station (CMD,TEAM_ID,COMMAND_NAME,ARGUMENTS)
    - It returns the command name and the arguments
    - The command name is used to call the appropriate function
    """
    command = str(command).split(",")
    command_name = command[2]
    arguments = command[3:]
    return command_name, arguments


def get_GPS_time():
    """
    This function will get the GPS time
    """
    GPS_time = sensors.GPS_time
    return GPS_time


def set_CANSAT_time(UTC_time=None):
    """
    This function will set the CANSAT time to UTC
    """
    if type(UTC_time) == str:
        my_date = datetime.date(datetime.now(timezone.utc)).strftime("%Y-%m-%d")
        UTC_time = datetime.strptime(my_date + " " + UTC_time, "%Y-%m-%d %H:%M:%S")

    global gl_mission_time, gl_mission_init_time, gl_system_init_time
    gl_system_init_time = datetime.now(timezone.utc).replace(tzinfo=None)
    if UTC_time == None:
        UTC_time = get_GPS_time()

    gl_mission_time = UTC_time
    gl_mission_init_time = UTC_time
    return 0


def calibrate_altitude(parsed_sensor_data):
    """
    This function will set the altitude calibration
    """
    global gl_zero_altitude_pressure
    gl_zero_altitude_pressure = parsed_sensor_data["pressure"]
    return 0

def deploy_heatshield():
    """
    Function to deploy the heatshield
    """
    global gl_HS_deployed, gl_state
    gl_state = "Descent"
    gl_HS_deployed = True
    #################### UNCOMMENT LATER ####################
    HS_deploy_servo(gl_HS_deploy_servo_angle)
    # #######################################################


def deploy_parachute():
    """
    Function to deploy the parachute
    """
    global gl_PC_deployed, gl_state
    gl_state = "Landing"
    gl_PC_deployed = True
    #################### UNCOMMENT LATER ####################
    parachute_servo(gl_parachute_servo_angle)
    #########################################################


def turn_beacon_off():
    """
    Function to turn off the beacon
    """
    global gl_beacon_status
    gl_beacon_status = "OFF"
    #################### UNCOMMENT LATER ####################
    beacon_off()
    # #######################################################


def turn_beacon_on():
    """
    Function to turn on the beacon
    """
    global gl_beacon_status
    gl_beacon_status = "ON"
    #################### UNCOMMENT LATER ####################
    beacon_on()
    # #######################################################


def call_CANSAT_ops(command_name, arguments, parsed_sensor_data):
    """
    This function will call the appropriate function based on the command received.
    """
    global gl_telemtry_status, gl_previous_command, gl_mode, gl_simp_pressure, gl_exit
    
    if command_name == "CX":
        if arguments[0] == "ON":
            gl_telemtry_status = "ON"
        elif arguments[0] == "OFF":
            gl_telemtry_status = "OFF"
        else:
            print("Invalid argument for CX command")
            gl_send_error += "Invalid argument for CX command\n"
        gl_previous_command = f"CX {arguments[0]}"

    elif command_name == "ST":
        if arguments[0] == "GPS":
            set_CANSAT_time()
        else:
            set_CANSAT_time(arguments[0])
        gl_previous_command = f"ST {arguments[0]}"

    elif command_name == "CAL":
        calibrate_altitude(parsed_sensor_data)
        gl_previous_command = "CAL"

    elif command_name == "EXIT":
        gl_exit = True

    elif command_name == "BCN":
        if arguments[0] == "ON":
            turn_beacon_on()
        elif arguments[0] == "OFF":
            turn_beacon_off()
        else:
            gl_send_error += "Invalid argument for BCN command\n"
            print("Invalid argument for BCN command")
        gl_previous_command = f"BCN {arguments[0]}"

    elif command_name == "SIM":
        if arguments[0] == "ENABLE":
            gl_mode = "SIM-1"
        elif arguments[0] == "DISABLE":
            gl_mode = "Flight"
        elif arguments[0] == "ACTIVATE":
            if gl_mode == "SIM-1":
                gl_mode = "SIM"
            else:
                gl_send_error += "Enable simulation mode before using this command\n"
                print("Enable simulation mode before using this command")

        else:
            gl_send_error += "Invalid argument for SIM command\n"
            print("Invalid argument for SIM command")

    elif command_name == "SIMP":
        if gl_mode == "SIM":
            parsed_sensor_data["pressure"] = arguments[0]
            gl_simp_pressure = int(arguments[0])
        else:
            gl_send_error += "Enable simulation mode before using this command\n"
            print("Enable simulation mode before using this command")

    else:
        print("Invalid command")
        gl_send_error += "Invalid command\n"



def find_flight_state(parsed_sensor_data):
    """
    This function will find the flight state of the cansat
    """
    global gl_state, gl_max_altitude
    altitude = calculate_altitude_from_pressure(parsed_sensor_data["pressure"])
    gl_max_altitude = max(gl_max_altitude, altitude)

    if gl_max_altitude == 0 and altitude == 0:
        gl_state = "NA"

    elif altitude <= gl_max_altitude-5:
        gl_state = "Descent"
        ####################### This is there only in processor 1 #######################
        deploy_heatshield()
        #################################################################################

    elif altitude >= 4:
        gl_state = "Ascend"
    
    if gl_PC_deployed:
        gl_state = "Landing"

    if (gl_state == "Descent" and altitude <= 130):
        deploy_parachute()

    #################### This is there only in processor 2 ####################
    # if (gl_state == "Descent" and altitude <= 150):
    #     release_heatshield()
    ##########################################################################

    return gl_state


########################## PROCESSOR RESETS #################################
def save_through_reset():
    """
    This function will save the data through processor resets.
    Data that needs to be saved through processor resets:
    1. Mission time
    2. Altitude calibration
    3. Count of packets transmitted
    """
    with open(f"Save_reset_{gl_TEAM_ID}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [gl_system_init_time, gl_zero_altitude_pressure, gl_packets_sent])
    return 0


def load_values_from_save_reset():
    """
    This function will load the data from the save reset file
    and set the values of the global variables
    """

    global gl_zero_altitude_pressure, gl_packets_sent, gl_system_init_time
    with open(f"Save_reset_{gl_TEAM_ID}.csv", "r", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            gl_system_init_time = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
            gl_zero_altitude_pressure = int(row[1])
            gl_packets_sent = int(row[2])
    return 0


############################### MAIN FUNCTION ###########################
if __name__ == "__main__":
    # starting camera
    #################### UNCOMMENT LATER ####################
    # picam2.start_recording(encoder,output)
    # #######################################################

    save_through_reset()


    # Open CANSAT connection.
    ################### UNCOMMENT LATER #################
    gl_cansat.open()
    gl_cansat.set_pan_id(bytearray(PANID))
    gl_cansat.set_dest_address(GROUND_STATION_XBEE_64BIT_ADDRESS)
    gl_cansat.add_data_received_callback(data_receive_callback)
    ####################################################
    flag = False
    sensors = Sensors()

    # This is the loop of the flight software
    while True:
        if gl_exit:
            break

        load_values_from_save_reset()

        curr_time = current_mission_time()
        if curr_time - gl_prev_sampling_time <= timedelta(seconds=gl_sampling_time_period):
            continue

        # sensors = Sensors()
        sensors.get_values(True)
        parsed_sensor_data = get_sensor_data()        
        parsed_data = sensor_data_to_telemetry_format(parsed_sensor_data)
        gl_state = find_flight_state(parsed_sensor_data)
        
        if (gl_gnd_station_cmd != None and gl_gnd_station_cmd_time != gnd_station_prev_cmd_time):
            # update past ground station command time
            gnd_station_prev_cmd_time = gl_gnd_station_cmd_time
            command_name, arguments = parse_command(gl_gnd_station_cmd)
            call_CANSAT_ops(command_name, arguments, parsed_sensor_data)

        if gl_mode == "SIM":
            parsed_data["pressure"] = str(gl_simp_pressure)
            parsed_data["altitude"] = str(calculate_altitude_from_pressure(gl_simp_pressure))

        #################### ONLY IN P1 (Not necessary) #######################
        # send_to_P2(parsed_data)
        ######################################################
        cur_time = current_mission_time()
        
        # Send data to the ground station
        if gl_telemtry_status == "ON":
            if gl_prev_tel_time == None:
                if not (send_telemetry(parsed_data)):
                    gl_prev_tel_time = cur_time
                    gl_send_error = "All OK"
                else:
                    gl_send_error = "Unable to send telemetry data"

            elif cur_time - gl_prev_tel_time >= timedelta(seconds=gl_telemetry_time_period):
                if not (send_telemetry(parsed_data)):
                    gl_prev_tel_time = cur_time
                    gl_send_error = "All OK"
                else:
                    gl_send_error = "Unable to send telemetry data"

        # save the data through processor resets
        save_through_reset()


    ################################## UNCOMMENT LATER ###################################
    # stopping camera
    # picam2.stop_recording()

    # close XBEE connection
    gl_cansat.close()
    ######################################################################################


