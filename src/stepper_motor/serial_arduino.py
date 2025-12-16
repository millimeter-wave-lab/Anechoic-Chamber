#!/usr/bin/env python3
import time
import serial
import numpy as np

# Initializing serial comm variable
ser = None

def open_serial(serial_port):
    """
    Configures the serial connections (the parameters differs on the device you are connecting to)
    """
    global ser
    ser = serial.Serial(
        port=serial_port,
        baudrate=115200,bytesize=8, timeout=2, parity='N', stopbits=1)

def is_serial_open():
    """
    Returns whether the serial port is open or not
    """
    return ser.isOpen()

def close_serial():
    """
    Closes the serial port
    """
    ser.close()

def send_cmd(id, cmd, cmd_data, wait_time):
    """
    Send command via serial
    """
    #print("Sent: "+ str(cmd)+", Length: " + str(len(cmd)))
    recv_ok = False
    response = bytearray()
    while not recv_ok:
        msg = "<" + str(id)+ "-" + str(cmd) + ":" + str(cmd_data)+">"
        msg_in_bytes = bytes(msg, 'utf-8')

        ser.write(msg_in_bytes)
        time.sleep(wait_time)
        while ser.inWaiting() > 0:
            response += bytearray(ser.read())

        #print("Received: " +str(response)+", Length: " + str(len(response)) +"\n")
        response_str = response.decode("utf-8")
        print(response_str)
        if response_str[:4+len(str(id))] == "<"+str(id)+"-ok":
            recv_ok = True
        else:
            response = bytearray()
            print("Did not receive correct answer, retrying...")


    return response_str


# for CRC calculations go to: https://www.lammertbies.nl/comm/info/crc-calculation
