######## figure out python script execution at boot

# Establish SSH between RPi and Laptop

# Initialising the Flight Software
- on the terminal of you laptop run the following command:
>> git pull https://github.com/Sreyas-03/MyFork_CANSAT-IIITH-2023.git
>> cd MyFork_CANSAT-IIITH-2023
>> scp -r Flight_Software <RPi port>:<Destination_directory>


## Necessary libraries to be downloaded on RPi
- Run these commands on RPi:
>> pip install digi-xbee
>> pip install smbus2
>> pip install picamera2
>> pip install pynmea2

## Command to run FSW on the RPi
- Run these commands on RPi:
>> python3 main_V2_P1.py

## Setting up the RPi:
- I2C needs to be enabled
>> sudo raspi-config
[on the GUI, enable I2C and Serial]
[Serial login enable - NO]
[Serial hardware enable - YES]
- Verify the port to which XBEE is connected to RPi, and change in the connected
[uncomment Line 119 or 120 depending on this]

## To close the FSW - type the command "EXIT" in the command line in the dashboard and hit "Send"


# Ground Station Setup

- connect the XBEE to the laptop and change the port to "COM3"
[line number - 124 Dashboard/main.py]

## Libraries Required
>> pip insall flask
>> pip install digi-xbee

## To run the dashboard
Perform the following commands on your laptop terminal:
>> cd Dashboard
>> python3 app.py