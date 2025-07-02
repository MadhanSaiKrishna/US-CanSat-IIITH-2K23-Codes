# Plots we need to make
"""
# STATIC PLOTS:
-------------------------------
1. mission_time - static value
2. packet_count - static value
3. mode - static value
4. state - static value
7. HS_deployed - static value
8. PC_deployed - static value
12. GPS_time - static value
14. GPS_latitude - static value
15. GPS_longitude - static value
16. GPS_sats - static value
17. tiltX - static value
18. tiltY - static value
19. rotZ - static value
20. command_echo - static value
21. optional_data - static value

# GRAPHS:
-------------------------------
5. altitude vs mission_time
6. air_speed vs mission_time
9. temperature vs mission_time
10. pressure vs mission_time
11. voltage vs mission_time
13. GPS_altitude vs mission_time
"""


import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import Data
import matplotlib.dates as mdates
from matplotlib.table import Table
from datetime import datetime, timedelta

############## dummy imports for fake data ##############
import random
#########################################################

# Initialize plots
# The axis and plot names start with gl_ to indicate that they are global variables
gl_fig, ((gl_ax_alttitude, gl_ax_air_speed), (gl_ax_temperature,
         gl_ax_pressure), (gl_ax_voltage, gl_ax_GPS_altitude)) = plt.subplots(3, 2)

gl_axes = {
    5: gl_ax_alttitude,
    6: gl_ax_air_speed,
    9: gl_ax_temperature,
    10: gl_ax_pressure,
    11: gl_ax_voltage,
    13: gl_ax_GPS_altitude
}

gl_titles = {
    5: "Altitude (m)",
    6: "Air Speed (m/s)",
    9: "Temperature (°C)",
    10: "Pressure (Pa)",
    11: "Voltage (V)",
    13: "GPS Altitude (m)"
}

gl_graphs = [5, 6, 9, 10, 11, 13]
gl_static = [1, 2, 3, 4, 7, 8, 12, 14, 15, 16, 17, 18, 19, 20, 21]


gl_data_pts = []
gl_lines = {}
for idx in gl_graphs:
    line, = gl_axes[idx].plot([], [], label='Data')
    gl_lines[idx] = line

plt.tight_layout(pad=0.5)
plt.subplots_adjust(top=0.9, bottom=0.1, left=0.1, right=0.9, hspace=0.5, wspace=0.5)



def get_latest_data(frame, datapt):
    gl_data_pts.append(datapt)
    updated = update_statics(datapt)
    assert updated == 0, "Statics not updated"
    updated = update_graphs(frame)
    assert updated == 0, "Graphs not updated"
    return 0

def update_statics(latest_data):
    # Update the static plots
    table_data = []
    for idx in gl_static:
        key = [k for k, v in Data.attribute_idx.items() if v == idx][0]
        table_data.append([key, latest_data.idx_attribute[idx]])

    # print(latest_data.mission_time)
    # print(latest_data.packet_count)
    # print(latest_data.mode)
    # print(latest_data.state)
    # print(latest_data.HS_deployed)
    # print(latest_data.PC_deployed)
    # print(latest_data.GPS_time)
    # print(latest_data.GPS_latitude)
    # print(latest_data.GPS_longitude)
    # print(latest_data.GPS_sats)
    # print(latest_data.tiltX)
    # print(latest_data.tiltY)
    # print(latest_data.rotZ)
    # print(latest_data.command_echo)
    # print(latest_data.optional_data)
    return 0

def update_graph_idx(frame, idx, max_points=20):
    if len(gl_data_pts) > max_points:
        gl_data_pts.pop(0)

    x_data = [mdates.date2num(datetime.strptime(data.mission_time, "%H:%M:%S")) for data in gl_data_pts]
    y_data = [data.idx_attribute[idx] for data in gl_data_pts]
    # print(x_data)

    gl_lines[idx].set_data(x_data, y_data)
    gl_axes[idx].relim()
    gl_axes[idx].autoscale_view()
    gl_axes[idx].set_title(gl_titles[idx])
    gl_axes[idx].tick_params(axis='x', rotation=45)
    gl_axes[idx].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    gl_lines[idx].set_linewidth(2)
    return 0

def update_graphs(frame):
    for idx in gl_graphs:
        updated = update_graph_idx(frame, idx)
        assert updated == 0, "Graph not updated"
    return 0


# ani = FuncAnimation(gl_fig, get_latest_data, interval=1000)
# plt.show()