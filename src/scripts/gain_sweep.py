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

GEN_POWER = 20
CURVE_POINTS = 1000
RES_BW = 75e3 # 75 kHz
VID_BW = 30e3 # 30 kHz
SWEEP_TIME = 10e-3

# Initializing spectrum analizer ethernet communication
visaname = 'TCPIP0::10.17.90.141::inst0::INSTR'
siglent = sva1075x.sva1075x(visaname)

# Configuring spectrum analizer Parameters
pts = CURVE_POINTS
freq = [1e9, 2e9]
res_bw = RES_BW
video_bw = VID_BW
sw_time = SWEEP_TIME
siglent.configure_spectrum(freq, pts, res_bw, video_bw, sw_time)


#Initializing gennerator ethernet communication
rm = pyvisa.ResourceManager("@py")
generator_IP = 'TCPIP::10.17.90.229::INSTR'
rf_psg = rm.get_instrument(generator_IP)
# Initializing radar motors, setting speeds and accelerations

def point_and_measure(measure_wait_time):

    measure_time = datetime.utcnow()

    # Waits for the radar curve to refresh
    time.sleep(measure_wait_time)
    spectra = siglent.get_spectra()

    return (measure_time, spectra)

sweep = np.arange(600, 3000, 50)
print(len(sweep))
spectrum = np.zeros(len(sweep))

time.sleep(1)

for i in range(len(sweep)):

    sweep_frequency = sweep[i]
    rfgen = rm.get_instrument(generator_IP)
    generator.give_freq_Mhz(rfgen, GEN_POWER, sweep_frequency, on = 1)
    time.sleep(0.1)
    siglent.configure_frequency(sweep_frequency * 1e6, 2e6)
    time.sleep(0.1)
    result = point_and_measure(0.1)
    spectrum[i] = np.max(result[1])

np.savetxt('gainsweep_2x2_directcombiner_otherpol.csv', spectrum, delimiter = ",", fmt = '%1.4f')
plt.plot(spectrum)
plt.show()
