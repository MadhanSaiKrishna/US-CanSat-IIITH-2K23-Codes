import numpy as np
import matplotlib.pyplot as plt

############## Fake Thermal and Vacuum Test ########
# def time():
#     return np.random.randint(0, 100)

# def f(r):
#     return 50 + 20*(r/20)**2 * np.exp(-r/20) + np.random.random()*2

# def p(r):
#     return 101325/(r**3) + 100 + np.random.random()*100

# h_b = 0 # Should be 625 (height above sea level actually)
# T_b = 298.15
# P_b = 98543
# L_b = -0.0065
# R = 8.31432
# g = 9.81
# M = 0.0289644
# def h(P):
#     return h_b + 0.0003*T_b/L_b * ((P/P_b)**(-R*L_b/(g*M)) - 1)

# n = 1.4
# R = 8314.47
# V = 30
# k = n*R/V



############## Dummy function to generate fake data ##############
# Ax, Ay, Az, Gx, Gy, Gz, T = 0, 0, 0, 0, 0, 0, 0
# data = []
# time_steps_to_display = 15

# def update(fake=False, temp_value=-1, pressure_value=-1):
#     for_cnt = 1
#     while for_cnt >0:
#         data = main.get_data()
#         # print(data)
#         data = data.get_parsed_data()
#         main.js_xValues.append(str(data[1]))
#         main.js_alt_Values.append(h(data[10]))
#         main.js_air_speed_Values.append(data[6])
#         if fake:
#             main.js_temperature_Values.append(temp_value)
#             main.js_pressure_Values.append(pressure_value)
#         else:
#             main.js_temperature_Values.append(data[9])
#             main.js_pressure_Values.append(data[10])
#         main.js_voltage_Values.append(data[11])
#         main.js_gps_altitude_Values.append(data[13])
#         main.js_combined_Values = [main.js_xValues[-1*min(len(main.js_xValues), time_steps_to_display) : ], 
#                                    main.js_alt_Values[-1*min(len(main.js_alt_Values), time_steps_to_display) : ], 
#                                    main.js_air_speed_Values[-1*min(len(main.js_air_speed_Values), time_steps_to_display) : ], 
#                                    main.js_temperature_Values[-1*min(len(main.js_temperature_Values), time_steps_to_display) : ], 
#                                    main.js_pressure_Values[-1*min(len(main.js_pressure_Values), time_steps_to_display) : ], 
#                                    main.js_voltage_Values[-1*min(len(main.js_voltage_Values), time_steps_to_display) : ], 
#                                    main.js_gps_altitude_Values[-1*min(len(main.js_gps_altitude_Values), time_steps_to_display) : ]
#                                 ]
#         for_cnt -= 1
#         for values in main.js_combined_Values:
#             data.append(values)

#     if main.gl_CX_state == 0:
#         data.append("CX ON")
#     else:
#         data.append("CX OFF")
    
#     if main.gl_BCN_state == 0:
#         data.append("BCN ON")
#     else:
#         data.append("BCN OFF")

#     return data


# data = update()
# print(data)

# # data = data.append(main.js_combined_Values)
# print(main.js_combined_Values)


# line_counter = 0
# theta_pitch, theta_roll = 0, 0   
# r = 1

############## Flask code for Fake Data for Testing ##############
# app = Flask(__name__)
# @app.route('/data_json')
# def data_json():
    ### Vibration Test ###
    # global line_counter
    # temp = 0
    # with open('readings_2.csv', 'r') as file:
    #     fake_data = file.readlines()
    #     fake_data = fake_data[line_counter].split(',')
    #     line_counter += 1
    #     theta_pitch, theta_roll = fake_data[7], fake_data[8]
    #     temp = fake_data[6]

    # data = update(fake=True, temp_value=temp, pressure_value=98543 + random.random()*10)
    # data[5] = (random.random())*0.5
    # data[17] = theta_pitch[:5]
    # data[18] = theta_roll[:5]
    # data[19] = 0.3 + random.random()*0.1


    ### Drop test ###
    # data = update()
    # data[5] = round(random.random()*0.05, 5)
    # data[17] = round(random.random()*0.05, 5)
    # data[18] = round(random.random()*0.05, 5)
    # data[19] = round(random.random()*0.02, 5)

    ### Thermal test ###
    # global r
    # data = update(fake=True, temp_value=f(r), pressure_value=k*(f(r) + 273))
    # data[5] = round(random.random()*0.05, 5)
    # data[17] = round(random.random()*0.05, 5)
    # data[18] = round(random.random()*0.05, 5)
    # data[19] = round(random.random()*0.02, 5)
    # r+=1

    ### Vacuum Test ###
    # global r
    # data = update(fake=True, pressure_value=p(r), temp_value=30+np.random.random()*0.3)
    # data[5] = round(random.random()*0.05, 5)
    # data[17] = round(random.random()*0.05, 5)
    # data[18] = round(random.random()*0.05, 5)
    # data[19] = round(random.random()*0.02, 5)
    # r+=1


    # return jsonify(data)