import numpy as np
import matplotlib.pyplot as plt

name = 'testnuevo'
data1 = np.loadtxt(name + '.csv', delimiter = ",")
data2 = np.loadtxt(name + '2.csv', delimiter = ",")
angles = np.loadtxt(name + 'angles.csv', delimiter = ",")
frequencies = np.loadtxt(name + 'frequencies.csv', delimiter = ",")
