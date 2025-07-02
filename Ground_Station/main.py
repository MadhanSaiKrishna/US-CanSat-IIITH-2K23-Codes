# this is the main file for the ground station
# it will run the GUI and the serial communication

# The objective of this program
"""
OBJECTIVES:
^^^^^^^^^^^

Serial io
-----------------------------------
1. get Serial data from the XBEE [X]
2. Count number of packets received [X]
3. Send commands to the FSW [X]
4. Upon simulation mode - send data to the CANSAT [X]

Data Processing
-----------------------------------
5. parse the data to find the commands and the data [X]
6. Save the data in a csv file [X]
7. Create commands to send to the PICO [X]

Data Visualization
-----------------------------------
8. Plot the data [X]
9. Display the plots on a simple webpage [X]

Altitude Calibration
-----------------------------------
10. Send command for calibrate alitiude before launch [X]

11. Maintain 0 Calibration in case of processor reset [O]
-- thinking of creating a file in the PICO to store the calibration data, so will be handled in FSW

Simulation
-----------------------------------
12. Upon simulation mode - get data from the simulation file [X]
"""


"""
TODO
1. Check data validity of recived XBEE data - [S] (S for skip)
2. Write a function to write fields in the csv file - [X]
3. Complete send_command function - [T] (T for to be tested)
4. Set an interupt of 1 second to send SIMP - [X] 
5. Complete send_sim_pressure function - [X] (open the csv file globally)
6. Change return code (in case of failure) for all send_commands - [S] (based on ECHO_CMD)
7. Processor reset - temp file to frontend pipeline - [X]
8. Write plot generation code from csv file - []
"""

# import libraries
import csv

import Data
import plots
import commands
import json

from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress # XBee

############## dummy imports for fake data ##############
import random
from datetime import datetime
gl_cnt = 0
#########################################################

# errors
ER_ACTSIM_BEF_ENSIM = -1
ER_INVALID_SIM_MODE = -2

######################## Global constants (gl stands for global) ###############
gl_TEAM_ID = 2085
gl_sim_filename = "sim_data.csv"
gl_sim_file = open(gl_sim_filename, "r")   #sim stands for simulation
gl_sim_line_no = 0

gl_temp_telemetry_filename = "temp_telemetry.json"
gl_telemetry_filename = f"Flight_{gl_TEAM_ID}.csv"

with open(gl_telemetry_filename, "w", newline="") as f:
    writer = csv.writer(f)
    headers = Data.attribute_idx.keys()
    writer.writerow(headers)


######################## Global variables ##########################
gl_enable_sent = False
gl_sim_mode = True

# For app.py
gl_count = 0 # counts the number of packets received
gl_CX_state = 0
gl_BCN_state = 0

gl_parsed_data = {}
js_xValues = []
js_alt_Values = []
js_air_speed_Values = []
js_temperature_Values = []
js_pressure_Values = []
js_voltage_Values = []
js_gps_altitude_Values = []
js_combined_Values = []
time_steps_to_display = 10

js_graph_keys = ["xValues", "alt_Values", "air_speed_Values", "temperature_Values", "pressure_Values", "voltage_Values", "gps_altitude_Values"]

gl_cansat_telemetry = ""
gl_cansat_telemetry_time = ""
# gl_default_telemetry = f"2085,{datetime.now().second},{gl_count},NA,NA,-1,-1,NA,NA,-1,-1,-1,00:00:00,-1,-1,-1,-1,-1,-1,-1,NA,NA,NA,NA,END_TELEMETRY"

############################## XBEE ################################

# XBee Settings for GCS
GROUND_STATION_64BIT_ADDRESS_STRING = "0013A200410908BE"
GROUND_STATION_XBEE_64BIT_ADDRESS = XBee64BitAddress.from_hex_string(GROUND_STATION_64BIT_ADDRESS_STRING)

# XBee Settings for CanSat XBEE
REMOTE_XBEE_64BIT_ADDRESS = "0013A2004106F519"
CANSAT_XBEE_64BIT_ADDRESS = XBee64BitAddress.from_hex_string(REMOTE_XBEE_64BIT_ADDRESS)

# GCS Settings
GCS_PORT = "/dev/tty.usbserial-00000000" # Update based on system
GCS_BAUD_RATE = 9600
PANID = b"\x20\x85" # HEX 2085

gl_received = False        # Becomes true upon receiving data
gl_received_message = None # String containing the data received
gl_received_fragments = [] # To concatenate the data segments received during XBEE transmission
gl_max_fragments = 2

# Callback function for receiving data
def data_receive_callback(xbee_message):
    """
    Function which is called when XBEE receives data
    """
    
    global gl_received, gl_received_message, gl_received_fragments, gl_parsed_data
    gl_received = False
    # address = xbee_message.remote_device.get_64bit_addr()
    data = xbee_message.data.decode("utf8")
    gl_received_fragments.append(data)
    
    if "END_TELEMETRY" in data:
        gl_received = True
        gl_received_message = ",".join(gl_received_fragments)
        gl_received_fragments = []
        # print(f"Received data from {address}: {gl_received_message}")
          
    # Not true in general
    elif len(gl_received_fragments) > gl_max_fragments:
        print("Error in transmission. Telemetry lost.")

    datapt = gl_received_message.split(',')[:-1]
    data = Data.Data(datapt)
    datapt = data.get_parsed_data()
    data_validity = check_datapt_validity(datapt)
    
    if data_validity == True:
        if check_if_new_data(datapt):
            clear_temp_data_from_file()
            gl_count += 1
            save_data(datapt)
        gl_parsed_data = write_temp_data_to_file(datapt)
    return 0


##################### UNCOMMENT LATER ###################################
# gl_gnd_station = XBeeDevice(GCS_PORT, GCS_BAUD_RATE)
# gl_cansat = RemoteXBeeDevice(gl_gnd_station, CANSAT_XBEE_64BIT_ADDRESS)

# # Set callback function i.e. function to call upon receiving data
# gl_gnd_station.add_data_received_callback(data_receive_callback)
##########################################################################



########################### Data Processing ############################

def check_datapt_validity(datapt):
    """
    This function will check the validity of the data received from serial port.
    Check for data type and ranges (later)
    """
    return True


def get_data():
    """
    This function will get the data from the XBEE
    """
    global gl_count
    datapt = gl_received_message.split(',')[:-1]

    # For random data
    # data = generate_data()
    # data_validity = check_datapt_validity(data)

    data = Data.Data(datapt)
    datapt = data.get_parsed_data()
    data_validity = check_datapt_validity(datapt)
    
    if data_validity == True:
        gl_count += 1
        save_data(datapt)

    # if data_validity == True:
    #     if check_if_new_data(datapt):
    #         clear_temp_data_from_file()
    #     gl_count += 1
    #     save_data(datapt)
    #     gl_parsed_data = write_temp_data_to_file(datapt)
    
    # print(datapt)
    return datapt


def save_data(parsed_data):
    """
    This function will save the data in the csv file - Flight_<teamID>.csv
    """

    with open(gl_telemetry_filename, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(list(parsed_data.values())[:-2])
    return 0


########################### COMMANDS ###############################
def send_command(command):
    """
    This function will send the command to the PICO.
    Command format - (CMD,TEAM_ID,COMMAND)
    """
    try:
        gl_gnd_station.send_data(gl_cansat, command)
    except:
        # print("Error in sending data.")
        print(command)
        return 1
    return 0


def calibrate_altitude():
    """
    Command call to calibrate altitude to 0
    """
    cmd = commands.Command(gl_TEAM_ID)
    CAL = cmd.create_CAL()
    Sent = send_command(CAL)
    return 0


def set_time(UTC=False, GPS=False):
    """
    Command call to set time to UTC
    """
    cmd = commands.Command(gl_TEAM_ID)
    ST = cmd.create_ST(UTC, GPS)
    assert ST != commands.ER_ST_INVALID_INPUT
    assert ST != commands.ER_ST_NOTIME_AND_NOGPS
    assert ST != commands.ER_ST_TIME_AND_GPS
    Sent = send_command(ST)
    return 0


def toggle_beacon():
    """
    Command call to toggle the audio beacon
    """
    global gl_BCN_state
    gl_BCN_state = 1 - gl_BCN_state
    cmd = commands.Command(gl_TEAM_ID)
    BCN = cmd.create_BCN(gl_BCN_state)

    assert BCN != commands.ER_BCN_INVALID_STATUS
    Sent = send_command(BCN)
    return 0


def toggle_telemetry():
    """
    Command call to enable the telemetry
    """
    global gl_CX_state
    gl_CX_state = 1 - gl_CX_state
    print(gl_CX_state)
    cmd = commands.Command(gl_TEAM_ID)

    CX = cmd.create_CX(gl_CX_state)
    assert CX != commands.ER_CX_INVALID_STATUS
    Sent = send_command(CX)
    return 0


def enable_simulation():
    """
    Command call to enable the simulation mode.
    """

    global gl_enable_sent
    cmd = commands.Command(gl_TEAM_ID)
    SIM_E = cmd.create_SIM("ENABLE")
    assert SIM_E != commands.ER_SIM_INVALID_STATUS
    
    Sent = send_command(SIM_E)
    gl_enable_sent = True    
    return 0


def activate_simulation():
    """
    Command call to activate the simulation mode.
    """
    global gl_enable_sent, gl_sim_mode
    if gl_enable_sent == False:
        return ER_ACTSIM_BEF_ENSIM
    
    cmd = commands.Command(gl_TEAM_ID)
    SIM_A = cmd.create_SIM("ACTIVATE")
    assert SIM_A != commands.ER_SIM_INVALID_STATUS
    Sent = send_command(SIM_A)
    gl_enable_sent = False
    gl_sim_mode = True
    return 0


def get_next_sim_pressure():
    """
    This function will get the next pressure data from the simulation file.
    It will return the pressure data.
    """
    global gl_sim_line_no
    
    with open(gl_sim_filename, "r") as sim_file:
        reader = csv.reader(sim_file)
        for i, line in enumerate(reader):
            if i == gl_sim_line_no:
                gl_sim_line_no += 1
                return line[0]
    return 0


def send_sim_pressure():
    """
    Command call to send the simulation pressure to CanSat.
    """
    if gl_sim_mode == False:
        return 0
    
    elif gl_sim_mode == True:
        pressure = get_next_sim_pressure()
        pressure = round(float(pressure), 1)
        cmd = commands.Command(gl_TEAM_ID)
        SIM_P = cmd.create_SIMP(pressure)
        assert SIM_P != commands.ER_SIM_INVALID_STATUS
        Sent = send_command(SIM_P)
        return 0
    
    else:
        return ER_INVALID_SIM_MODE


########################### Processor Resets ########################

def check_if_new_data(parsed_data):
    """
    This function checks if the new data received is for a different time step from the data that is stored in the temp file.
    If the new data is for a different time step, return 1
    """

    # If the file has some json content. Read and store this json as a dictionary in d
    d = {}
    with open(gl_temp_telemetry_filename, "r") as f:
        d = json.load(f)

    if("mission_time" not in d.keys()): 
        return 0
    elif parsed_data["mission_time"] != d["mission_time"]: 
        return 1
    return 0


def write_temp_data_to_file(parsed_data):
    """
    Writes data into a temporary file
    This is done to handle processor resets from the ground station side,
    avoiding any complexity in the flight software.
    """
    d = {}
    # the file has some json content. Read and store this json as a dictionary in d
    with open(gl_temp_telemetry_filename, "r") as f:
        d = json.load(f)
    
    # add the new data to the dictionary
    for i in parsed_data.keys():
        if i in d.keys():
            pass
        else:
            d[i] = parsed_data[i]
    
    # write the dictionary back to the file
    with open(gl_temp_telemetry_filename, "w", newline="") as f:
        json.dump(d, f)
    return d


def clear_temp_data_from_file():
    d = {}
    with open(gl_temp_telemetry_filename, "w", newline="") as f:
        json.dump(d, f)
    return 0


###################### Function to generate fake data #################
def generate_data():
    global gl_cnt
    gl_cnt += 1
    time = datetime.now().strftime("%H:%M:%S")
    time = str(time)
    
    data = [gl_TEAM_ID, time, gl_count, 'F', 'RELEASED', (random.random())*0.05, 7.2+(random.random())*0.5, 'P', 'N', 25.2+(random.random())*0.05, 98542+(random.random())*5, 9+(random.random())*0.5, time, 536.21 + random.random()*0.2, 17.4065, 78.4772, 4, 23.01+(random.random())*5, 54.02+(random.random())*5, 12.1+(random.random())*5, 'CXON', "NA", "NA",'NA']
    # print(data[5])
    data1 = {}
    for i in range(len(data)):
        data1[i] = str(data[i])
    return data
    # datapt = Data.Data(data1)
    # return datapt.get_parsed_data()

##################################################################


# def start_CANSAT():
#     # This function will calibrate the CANSAT altitude to 0, and do other necessary start procedures
#     """
#     Requirements of start procedure is to be figured out
#     -----------------------------------------------------
#     1. Calibrate altitude to 0 [X]
#     2. Set the time [X]
#     3. Enable telemetry [?]
#     """
#     CAL_ret = calibrate_altitude()
#     set_time(UTC=True, GPS=False)
#     return 0