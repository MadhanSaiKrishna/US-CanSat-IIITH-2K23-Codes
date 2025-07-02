"""
This file is for the commands that will be sent to the PICO
"""

# import modules
from datetime import datetime,timezone

# Error Codes
ER_CX_INVALID_STATUS = 1
ER_ST_TIME_AND_GPS = 2
ER_ST_NOTIME_AND_NOGPS = 3
ER_ST_INVALID_INPUT = 4
ER_BCN_INVALID_STATUS = 5
ER_SIM_INVALID_STATUS = 6

class Command:
    def __init__(self, teamID):
        self.teamID = teamID

    def create_CX(self, status):
        """
        - CX command is to turn ON/OFF the telemetry transmissions
        - format : CMD,<team_ID>,CX,ON|OFF
        """
        if status == 1:
            status = "ON"
        elif status == 0:
            status = "OFF"
        else:
            return ER_CX_INVALID_STATUS
        return f"CMD,{self.teamID},CX,{status}"
    
    def create_ST(self, UTC=False, GPS=False):
        """
        - TS command is to set the time of the CANSAT
        - format : CMD,<team_ID>,ST,<hh:mm:ss> --> sets the CANSAT time to the given time
                   CMD,<team_ID>,ST,GPS --> sets the CANSAT time to the GPS time
        """

        if GPS == True:
            if UTC == True:
                return ER_ST_TIME_AND_GPS
            else:
                return f"CMD,{self.teamID},ST,GPS"
            
        if GPS == False:
            if UTC == False:
                return ER_ST_NOTIME_AND_NOGPS
            elif UTC == True:
                UTC_time = datetime.now(timezone.utc)
                UTC_time = UTC_time.strftime('%H:%M:%S')
                return f"CMD,{self.teamID},ST,{UTC_time}"
            else:
                return ER_ST_INVALID_INPUT

        else:
            return ER_ST_INVALID_INPUT

    def create_CAL(self):
        """
        - CAL command is to calibrate the altitude to 0 before the launch
        - format : CMD,<team_ID>,BCN,ON|OFF
        """
        return f"CMD,{self.teamID},CAL"
    
    def create_BCN(self, status):
        """
        - BCN command is to turn ON/OFF the audio beacon
        - format : CMD,<team_ID>,BCN,ON|OFF
        """
        if status == 1:
            status = "ON"
        elif status == 0:
            status = "OFF"
        else:
            return ER_BCN_INVALID_STATUS
        return f"CMD,{self.teamID},BCN,{status}"
    
    def create_SIM(self, status):
        """
        - SIM command is to enable, activate or deactivate the simulation mode
        - format : CMD,<team_ID>,SIM,ENABLE|ACTIVATE|DEACTIVATE
        """
        if status == "ENABLE":
            status = "ENABLE"
        elif status == "ACTIVATE":
            status = "ACTIVATE"
        elif status == "DISABLE":
            status = "DISABLE"
        else:
            return ER_SIM_INVALID_STATUS
        return f"CMD,{self.teamID},SIM,{status}"
    
    def create_SIMP(self, pressure):
        """
        - SIMP command is to send pressure data to the CANSAT from simulation_pressure_file
        - format : CMD,<team_ID>,SIMP,<pressure>
        """
        return f"CMD,{self.teamID},SIMP,{pressure}"