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

def point_and_wait(motor, angle, measure_wait_time):

    motor.move(angle)
    # Wait for motors to reach target angle
    motor.wait_for_target_angle(angle)
    measure_time = datetime.utcnow()

    # Waits for the radar curve to refresh
    print("Arrived to position, waiting " + str(measure_wait_time) + " s for radar curve to refresh")
    time.sleep(measure_wait_time)

    print("Motor at angle = " + str(angle))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'moves the radar to its 13 '+
                                                 'positions and logs the info')
    parser.add_argument('arduino_usb_port', help = 'arduino usb port for serial comm, tipically /dev/ttyUSB1')
    parser.add_argument('-swt','--sweep_time', type = float, default = 10, help ='sweep time in ms. 10 ms by default')
    parser.add_argument('-wait','--sa_wait_time', type = int, default = 1.5, help = 'Spectrum analizer wait time, in seconds, before taking the curve')

    args = parser.parse_args()

    # # Defining the sweep time
    try:
        SWEEP_TIME = args.sweep_time * 1e-3
    except:
        SWEEP_TIME = 10e-3

    # Defining wait time for radar
    measure_wait_time = args.sa_wait_time

    print("Using " + str(measure_wait_time) + " seconds wait time")
    time.sleep(1)

    serial_arduino.open_serial(args.arduino_usb_port)
    if serial_arduino.is_serial_open():
        print("Serial arduino port open succesfully")
    else:
        print("Could not open arduino radar port, FATAL ERROR")

    motor_Z = stepper_motor.stepper_motor(id = 1, speed = 0, max_speed = 400, acceleration = 100)
    motor_X = stepper_motor.stepper_motor(id = 2, speed = 0, max_speed = 400, acceleration = 100)

    motor_Z.set_motor_max_speed(100)
    motor_Z.set_motor_speed(0)
    motor_Z.set_motor_acceleration(100)
    time.sleep(1)

    motor_X.set_motor_max_speed(100)
    motor_X.set_motor_speed(0)
    motor_X.set_motor_acceleration(100)
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
                # motor_Z.move(target)
                motor_X.move(target)
            elif cmd == 'start':
                # motor_Z.set_offset_zero()
                motor_X.set_offset_zero()
                time.sleep(1)
                start = True
            else:
                print("Unknown command, try again. For ex: move 90")
        except:
            if inp == 'start':
                motor_Z.set_offset_zero()
                motor_X.set_offset_zero()
                time.sleep(1)
                start = True
            else:
                print("Unknown command, try again. For ex: move 90")

    # Pointing and measuring the corresponding angles
    print("YOU HAVE 180 SECONDS TO LEAVE THE ROOM!")
    time.sleep(1)
    start_time = time.time()

    angles = 360

    target_angle = 0

    # while target_angle <= 360:
    #
    #     point_and_wait(target_angle, measure_wait_time)
    #
    #     target_angle += 0.5
    for i in range(0, angles + 1):

        # point_and_wait(motor_Z, i, measure_wait_time)
        point_and_wait(motor_X, i, measure_wait_time)

    for i in range(angles, -1, -1):

        # point_and_wait(motor_Z, i, measure_wait_time)
        point_and_wait(motor_X, i, measure_wait_time)

        # target_angle += 5

    total_time = time.time()-start_time
    print("The measurement took " + str(total_time) + " seconds")
    # Done, returning motors to 0 position
    # motor.move(0)
    # Closing serial communication
    #serial_radar.close_serial()

    # Resetting motors
    #az_motor.reset()
    #el_motor.reset()

    # Printing results
    print("Measure OK")
    #print(measured_spectra)
