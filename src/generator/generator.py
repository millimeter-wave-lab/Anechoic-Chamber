import numpy as np
import matplotlib.pyplot as plt
import pyvisa

def give_freq_Mhz(rf_psg, power, freq_MHz, on = 1):

    pow_lev = power
    frequencyRF = freq_MHz * 1e6

    rf_psg.write('POW %f dBm' % pow_lev)
    rf_psg.write('FREQ %f Hz' % frequencyRF)

    if on == 1:
        rf_psg.write('OUTP on')
    else:
        rf_psg.write('OUTP off')
