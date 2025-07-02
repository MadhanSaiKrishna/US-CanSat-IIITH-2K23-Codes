from flask import Flask, render_template, jsonify, request, redirect, url_for
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress
from datetime import datetime, timedelta

import sys
sys.path.insert(0,'../Ground_Station')
import Data
import main



################### GCS Helper Function ###################
def update():
    for_cnt = 1
    while for_cnt >0:
        data = main.get_data()
        main.js_xValues.append(str(data["mission_time"]))
        main.js_alt_Values.append(data["altitude"])
        main.js_air_speed_Values.append(data["air_speed"])
        main.js_temperature_Values.append(data["temperature"])
        main.js_pressure_Values.append(data["pressure"])
        main.js_voltage_Values.append(data["voltage"])
        main.js_gps_altitude_Values.append(data["GPS_altitude"])
        main.js_combined_Values = [main.js_xValues[-1*min(len(main.js_xValues), main.time_steps_to_display) : ], 
                                   main.js_alt_Values[-1*min(len(main.js_alt_Values), main.time_steps_to_display) : ], 
                                   main.js_air_speed_Values[-1*min(len(main.js_air_speed_Values), main.time_steps_to_display) : ], 
                                   main.js_temperature_Values[-1*min(len(main.js_temperature_Values), main.time_steps_to_display) : ], 
                                   main.js_pressure_Values[-1*min(len(main.js_pressure_Values), main.time_steps_to_display) : ], 
                                   main.js_voltage_Values[-1*min(len(main.js_voltage_Values), main.time_steps_to_display) : ], 
                                   main.js_gps_altitude_Values[-1*min(len(main.js_gps_altitude_Values), main.time_steps_to_display) : ]
                                ]
        for_cnt -= 1
        for idx in range(len(main.js_combined_Values)):
            data[main.js_graph_keys[idx]] = main.js_combined_Values[idx]

    if main.gl_CX_state == 0:
        data["CX_btn"] = "CX ON"
    else:
        data["CX_btn"] = "CX OFF"
    
    if main.gl_BCN_state == 0:
        data["BCN_btn"] = "BCN ON"
    else:
        data["BCN_btn"] = "BCN OFF"

    return data


def CX_function():
    print("CX Button was clicked!")
    main.toggle_telemetry()
    return main.gl_CX_state
    # Use commands functions to send the command to the PICO

def ST_function():
    main.set_time(UTC=True, GPS=False)
    print("ST Button was clicked!")
    

def SE_function():
    main.enable_simulation()
    print("SE Button was clicked!")

def SA_function():
    main.activate_simulation()
    print("SA Button was clicked!")

def CAL_function():
    main.calibrate_altitude()
    print("CAL Button was clicked!")

def BCN_function():
    main.toggle_beacon()
    print("BCN Button was clicked!")
    


####################### Flask Code #######################
app = Flask(__name__)

@app.route('/', methods=["POST", "GET"])
def index():
    data = data_json()
    if request.method == "POST":
        command_rec = request.form['cmd']
        Sent = main.send_command(command_rec)
        print(command_rec)
        return render_template('index.html', data=data.json)
    if request.method == "GET":
        return render_template('index.html', data=data.json)

    return render_template('index.html', data=data.json)


@app.route('/data_json')
def data_json():
    # Waiting for received telemetry data
    main.gl_received = False
    start_time = datetime.now()
    while (main.gl_received is False):
        if datetime.now() - start_time > timedelta(seconds=1):
            # print("No data received.")
            main.gl_received_message = f"2085,{datetime.now().strftime("%H:%M:%S")},{main.gl_count},NA,NA,-1,-1,NA,NA,-1,-1,-1,00:00:00,-1,-1,-1,-1,-1,-1,-1,NA,NA,NA,NA,END_TELEMETRY"
            main.gl_count -= 1
            break
        else:
            continue
      
    # print("Received data: ", main.gl_received_message)
    data = update()
    return jsonify(data)



@app.route('/SIMP_call')
def SIMP_call():
    """
    Function to send Simulation Pressure to FSW every second
    """
    main.send_sim_pressure()
    return jsonify({})
    # return redirect(url_for('index'))

@app.route('/CX_call', methods=['POST'])
def CX_call():
    CX_function()
    return redirect(url_for('index'))


@app.route('/ST_call', methods=['POST'])
def ST_call():
    ST_function()
    return redirect(url_for('index'))


@app.route('/SE_call', methods=['POST'])
def SE_call():
    SE_function()
    return redirect(url_for('index'))

@app.route('/SA_call', methods=['POST'])
def SA_call():
    SA_function()
    return redirect(url_for('index'))

@app.route('/CAL_call', methods=['POST'])
def CAL_call():
    CAL_function()
    return redirect(url_for('index'))

@app.route('/BCN_call', methods=['POST'])
def BCN_call():
    BCN_function()
    return redirect(url_for('index'))



if __name__ == '__main__':
    
    # Open CANSAT connection with XBEE (Uncomment later)
    # main.gl_gnd_station.open()
    # main.gl_gnd_station.set_pan_id(bytearray(main.PANID))
    
    # Start the flask function
    app.run()

    # Close CANSAT connection. (Uncomment later)
    # main.gl_gnd_station.close()
    print("XBEE Connection closed")