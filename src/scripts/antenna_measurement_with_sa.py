# Como correr esto: nos vamos a Anechoic chamber, y desde ahi
# corremos python3 -m src.scripts.antenna_measurement (sin .py) con
# los respectivos argumentos... en particular filename y arduino_usb_port:
# python3 -m src.scripts.antenna_measurement 'test.csv' '/dev/ttyUSB0'
# La alimentacion del motor es de 12 V, 0.17 A aprox.

# ejemplo:
# sudo python3 -m src.scripts.antenna_measurement 'test1.csv' '/dev/ttyUSB0' --no_siglent_measure
# poner --siglent_measure para medir y --real_time_plot para ver el patron en tiempo real
# al empezar poner move 151 para ir al 0 (el motor no esta alineado... asi que no hay que poner move 0)
# lo otro es que ese comando te llva a una posicion absoluta... es decir, move x lleva al motor
# a la posicion x (siempre la misma)... NO se mueve x grados con respecto a donde estaba
# Luego de que el motor este alineado, poner start


from src.vna import sva1075x
from src.generator import generator
from src.stepper_motor import serial_arduino
from src.stepper_motor import stepper_motor
import time
import math
from datetime import datetime, timedelta
import pickle as pkl
import argparse
import matplotlib.pyplot as plt
import numpy as np
import ipdb
import pyvisa

import serial.tools.list_ports
ports = serial.tools.list_ports.comports()

for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))

MOTOR_STATUS_POLLING_TIME = 0.1     # in seconds

WAIT_TIME_AFTER_MEASUREMENT = 0.1   # in seconds
LOWEST_EL_ANGLE = 30    # Angle between zenith and lowest el point to measure

sweep = [500, 3000]

def point_and_measure(angle, measure_wait_time, siglent_use):

    motor.move(angle)
    # Wait for motors to reach target angle
    motor.wait_for_target_angle(angle)
    measure_time = datetime.utcnow()

    # Waits for the radar curve to refresh
    print("Arrived to position, waiting " + str(measure_wait_time) + " s for radar curve to refresh")
    time.sleep(measure_wait_time)
    if siglent_use:
        spectra = siglent.get_spectra()
    else:
        spectra = 0

    print("Measured spectra at angle = " + str(angle))
    return (measure_time, angle, spectra)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'moves the radar to its 13 '+
                                                 'positions and logs the info')

    parser.add_argument('filename', help = 'name of the file')
    parser.add_argument('arduino_usb_port', help = 'arduino usb port for serial comm, tipically /dev/ttyUSB1')
    parser.add_argument('-spl','--steps_per_loop', help ='steps per loop', default = 360)
    parser.add_argument('-rbw','--res_bw', type = float, default = 100, help ='resolution bandwidth in kHz. 100 kHz by default')
    parser.add_argument('-vbw','--video_bw', type = float, default = 100, help ='video bandwidth in kHz. 100 kHz by default')
    parser.add_argument('-swt','--sweep_time', type = float, default = 10, help ='sweep time in ms. 10 ms by default')
    parser.add_argument('-cp','--curve_points', type = int, default = 751, help = 'number of pointer per curve. 1000 by default')
    parser.add_argument('-minf_ghz','--minimum_freq_ghz', type = float, default = 1, help = 'minimum frequency span in ghz')
    parser.add_argument('-maxf_ghz','--maximum_freq_ghz', type = float, default = 2, help = 'maximum frequency span in ghz')
    parser.add_argument('-wait','--sa_wait_time', type = int, default = 5, help = 'Spectrum analizer wait time, in seconds, before taking the curve')
    parser.add_argument('--siglent_measure', action = 'store_true',help = "write this if you want to use the spectrum analizer", default=True)
    # parser.add_argument('--gen_measure', action = 'store_true',help = "write this if you want to use the generator", default=True)
    parser.add_argument('--no_siglent_measure', dest = 'sa_measure', action = 'store_false', help = "write this if you DON'T want to use the spectrum analizer")
    parser.add_argument('-extra','--extra_angle', type = float, default = 0, help ='extra angle past 360 to measure')
    parser.add_argument('--real_time_plot', action = 'store_true',help = "write this if you want to plot in real time", default=False)
    # parser.add_argument('--gen_power', default = 20, help = 'Generator power in dBm')

    args = parser.parse_args()

    # Defining degree step
    try:
        STEPS_PER_LOOP = int(args.steps_per_loop)
        DEGREE_STEP = 360 / STEPS_PER_LOOP

        print('Using degree step = ' + str(DEGREE_STEP))
        time.sleep(1)
    except:
        DEGREE_STEP = 1

    # #Defining generator power
    # try:
    #     GEN_POWER = args.gen_power
    # except:
    #     GEN_POWER = 20

    # Defining the number of points
    try:
        CURVE_POINTS = args.curve_points
    except:
        CURVE_POINTS = 751

    # # Defining the resolution bandwidth
    try:
        RES_BW = args.res_bw * 1e3
    except:
        RES_BW = 100e3 # 100 kHz

    # # Defining the video bandwidth
    try:
        VID_BW = args.video_bw * 1e3
    except:
        VID_BW = 100e3 # 100 kHz

    # # Defining the sweep time
    try:
        SWEEP_TIME = args.sweep_time * 1e-3
    except:
        SWEEP_TIME = 10e-3

    # Defining minimum freq span
    try:
        MIN_FREQ_default = sweep[0] * 1e6
    except:
        MIN_FREQ_default = sweep[0] * 1e6

    # Defining maximum freq span
    try:
        MAX_FREQ_default = sweep[1] * 1e6
    except:
        MAX_FREQ_default = sweep[1] * 1e6

    # Defining if plotting in real time
    real_time_plot = args.real_time_plot

    # Defining extra angle past 360 degrees measurement
    extra_angle = args.extra_angle

    # Defining wait time for radar
    measure_wait_time = args.sa_wait_time

    print("Using " + str(measure_wait_time) + " seconds wait time")
    time.sleep(1)

    # Defining if we are going to use the spectrum analizer to measure
    siglent_use = args.siglent_measure

    # Defining if we are going to use the spectrum analizer to measure
    # gen_use = args.gen_measure

    name = args.filename

    if (siglent_use):
        # Initializing spectrum analizer ethernet communication
        visaname = 'TCPIP0::10.17.90.141::inst0::INSTR'
        siglent = sva1075x.sva1075x(visaname)

        # Configuring spectrum analizer Parameters
        pts = CURVE_POINTS
        freq = [MIN_FREQ_default, MAX_FREQ_default]
        res_bw = RES_BW
        video_bw = VID_BW
        sw_time = SWEEP_TIME
        siglent.configure_spectrum(freq, pts, res_bw, video_bw, sw_time, manual_sweep = False)


    # #Initializing gennerator ethernet communication
    # rm = pyvisa.ResourceManager("@py")
    # generator_IP = 'TCPIP::10.17.90.229::INSTR'
    # rf_psg = rm.get_instrument(generator_IP)

    # Initializing radar motors, setting speeds and accelerations

    serial_arduino.open_serial(args.arduino_usb_port)
    if serial_arduino.is_serial_open():
        print("Serial arduino port open succesfully")
    else:
        print("Could not open arduino radar port, FATAL ERROR")

    motor = stepper_motor.stepper_motor(id = 1,speed = 0, max_speed = 400, acceleration = 100)

    motor.set_motor_max_speed(400)
    motor.set_motor_speed(0)
    motor.set_motor_acceleration(100)
    time.sleep(1)

    data_counter = 0

    # Waits until user inputs start
    start = False
    while(not start):
        inp = input("insert command to point antenna or to start (move x or start):")
        try:
            cmd, arg = inp.split(' ')
            if cmd == 'move':
                target = float(arg)
                motor.move(target)
            elif cmd == 'start':
                motor.set_offset_zero()
                time.sleep(1)
                start = True
            else:
                print("Unknown command, try again. For ex: move 90")
        except:
            if inp == 'start':
                motor.set_offset_zero()
                time.sleep(1)
                start = True
            else:
                print("Unknown command, try again. For ex: move 90")

    # Pointing and measuring the corresponding angles
    print("YOU HAVE 120 SECONDS TO LEAVE THE ROOM!")
    time.sleep(1)
    start_time = time.time()

    if (real_time_plot):

        fig = plt.figure()

        ax = plt.subplot(111, polar = True)
        plt.ion()
        plt.show()
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        power_plot = []
        plot_index = 0

    angles = STEPS_PER_LOOP
    spectrum = np.zeros((STEPS_PER_LOOP, pts))

    target_angle = -180
    for i in range(STEPS_PER_LOOP):

        meas = point_and_measure(target_angle, measure_wait_time, siglent_use)
        target_angle += DEGREE_STEP
        print(type(meas))
        print(len(meas))
        spectrum[i] = meas[2]

    # file = open(name,'ab')
    # measured_spectra = []
    # target_angle = 0
    # while abs(target_angle) <= 360 + extra_angle:
    #     result = point_and_measure(target_angle, measure_wait_time, siglent_use)
    #     target_angle += DEGREE_STEP
    #     pkl.dump(result,file)
    #     measured_spectra.append(result)
    #     if(real_time_plot):
    #         #ipdb.set_trace()
    #         target_point = int(CURVE_POINTS/2)
    #         aux = np.array(measured_spectra)
    #         angles_plot = np.array(aux[:,1]).astype(float)

    #         power_plot.append(aux[:,2][plot_index][1][target_point])
    #         freq_plot = aux[:,2][0][0]
    #         ax.cla()

    #         target_freq_ghz = round(freq_plot[1]/1e9*100)/100
    #         ax.set_title("Radiation pattern at " +str(target_freq_ghz) + " GHz", va='bottom')
    #         ax.plot(np.deg2rad(angles_plot), power_plot)

    #         fig.canvas.draw()
    #         fig.canvas.flush_events()
    #         plot_index +=1

    # file.close()



    np.savetxt('freq_axis_' + name, np.linspace(500,3000,751), delimiter = ",", fmt = '%1.4f')
    np.savetxt(name, spectrum, delimiter = ",", fmt = '%1.4f')

    total_time = time.time()-start_time
    print("The measurement took " + str(total_time) + " seconds")
    # Done, returning motors to 0 position
    motor.move(180)
    # Closing serial communication
    #serial_radar.close_serial()

    # Resetting motors
    #az_motor.reset()
    #el_motor.reset()

    # Printing results
    print("Measure OK")
    #print(measured_spectra)
