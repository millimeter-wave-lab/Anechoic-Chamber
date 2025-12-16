import time
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import pyvisa

from src.vna import sva1075x
from src.generator import generator

# =======================
# CONFIGURACIÓN INICIAL
# =======================
GEN_POWER = 20          # dBm
START_FREQ = 500        # MHz
STOP_FREQ = 1000        # MHz
STEP_FREQ = 1           # MHz
CURVE_POINTS = 1000
RES_BW = 75e3           # Hz
VID_BW = 30e3           # Hz
SWEEP_TIME = 10e-3      # s
SPAN = 2e6              # 2 MHz span alrededor de la frecuencia central
WAIT_TIME = 0.1         # s de espera entre seteo y medición

# =======================
# CONEXIÓN CON INSTRUMENTOS
# =======================
# Analizador de espectro
visaname = 'TCPIP0::10.17.90.141::inst0::INSTR'
siglent = sva1075x.sva1075x(visaname)
siglent.configure_spectrum([START_FREQ*1e6, STOP_FREQ*1e6], CURVE_POINTS, RES_BW, VID_BW, SWEEP_TIME)

# Generador de RF
rm = pyvisa.ResourceManager("@py")
generator_IP = 'TCPIP::10.17.90.229::INSTR'
rfgen = rm.get_instrument(generator_IP)

# =======================
# FUNCIÓN DE MEDICIÓN
# =======================
def point_and_measure(wait_time):
    """Toma una medición del analizador de espectro."""
    measure_time = datetime.utcnow()
    time.sleep(wait_time)
    spectra = siglent.get_spectra()
    return measure_time, spectra

# =======================
# BARRIDO DE FRECUENCIA
# =======================
sweep = np.arange(START_FREQ, STOP_FREQ + STEP_FREQ, STEP_FREQ)
spectrum = np.zeros(len(sweep))

print(f"Barrido de {START_FREQ} MHz a {STOP_FREQ} MHz en pasos de {STEP_FREQ} MHz ({len(sweep)} puntos)")

# Encender generador a potencia fija
generator.give_freq_Mhz(rfgen, GEN_POWER, START_FREQ, on=1)

# Pequeña espera inicial (opcional)
time.sleep(180)

for i, f in enumerate(sweep):
    # Configurar frecuencia del generador
    generator.give_freq_Mhz(rfgen, GEN_POWER, f, on=1)

    # Configurar analizador centrado en f MHz
    siglent.configure_frequency(f * 1e6, SPAN)

    # Medir
    _, trace = point_and_measure(WAIT_TIME)
    spectrum[i] = np.max(trace)

    if i % 500 == 0:  # imprimir cada 500 puntos para seguimiento
        print(f"[{i}/{len(sweep)}] Frecuencia: {f} MHz - Potencia pico: {spectrum[i]:.2f} dB")

# =======================
# GUARDAR Y GRAFICAR
# =======================
filename = f"gainsweep_big_PEC_{START_FREQ}MHz_{STOP_FREQ}MHz_{STEP_FREQ}MHzstep.csv"
np.savetxt(filename, spectrum, delimiter=",", fmt="%1.4f")
print(f"\n✅ Barrido completo. Datos guardados en '{filename}'")

plt.figure(figsize=(12,5))
plt.plot(sweep, spectrum)
plt.xlabel("Frecuencia [MHz]")
plt.ylabel("Potencia Pico [dB]")
plt.title("Respuesta en frecuencia")
plt.grid(True)
plt.tight_layout()
plt.show()

# Apagar generador al final (opcional)
generator.give_freq_Mhz(rfgen, GEN_POWER, STOP_FREQ, on=0)
