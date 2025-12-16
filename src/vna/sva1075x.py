import pyvisa, time
import numpy as np

class sva1075x():

    def __init__(self, visaname, sleep_time = 0.1):
        rm = pyvisa.ResourceManager()
        self.instr = rm.open_resource(visaname)
        self._sleep_time = sleep_time
        time.sleep(self._sleep_time)

    def configure_spectrum(self, freq, pts, res_bw, video_bw, sw_time, manual_sweep = True, attenuator = 0):
        """
            freq:       [initial_freq, end_freq] in Hz
            pts:        number of points    (the system does what it wants, only 751 points are available
            res_bw:     resolution bw in Hz
            video_bw:   video bw
            sw_time:    sweep time
        """

        self.set_instr_mode('sa')

        span = freq[1] - freq[0]
        central_freq = (freq[1] + freq[0]) / 2

        cmd = ":BWID %f Hz" % res_bw
        self.instr.write(cmd)
        time.sleep(self._sleep_time)

        cmd = "FREQ:SPAN %f Hz" % span
        self.instr.write(cmd)
        time.sleep(self._sleep_time)

        cmd = ":BWID:VID %f Hz" % video_bw
        self.instr.write(cmd)
        time.sleep(self._sleep_time)

        cmd = 'SWE:POIN %d' % pts
        self.instr.write(cmd)
        time.sleep(self._sleep_time)

        cmd = "FREQ:CENT %f Hz" % central_freq
        self.instr.write(cmd)
        time.sleep(self._sleep_time)

        cmd = ":POW:ATT %f" % attenuator
        self.instr.write(cmd)
        time.sleep(self._sleep_time)

        if manual_sweep:
            cmd = "SWEep:TIME %s" % sw_time
            self.instr.write(cmd)
            time.sleep(self._sleep_time)


    def configure_frequency(self, central_freq, span):

        cmd = "FREQ:SPAN %f Hz" % span
        self.instr.write(cmd)
        time.sleep(self._sleep_time)

        cmd = "FREQ:CENT %f Hz" % central_freq
        self.instr.write(cmd)
        time.sleep(self._sleep_time)

    def get_spectra(self, channel = 1):
        data = self.instr.query_ascii_values(':TRAC:DATA? ' + str(channel), container = np.array)
        return data

    def get_parameters(self):
        cmd = "BAND?"
        res_bw = self.instr.query_ascii_values(cmd)[0]
        cmd = "FREQ:SPAN?"
        span = self.instr.query_ascii_values(cmd)[0]
        cmd = 'BAND:VID?'
        video_bw = self.instr.query_ascii_values(cmd)[0]
        cmd = 'FREQ:CENT?'
        center = self.instr.query_ascii_values(cmd)[0]
        return res_bw, span, video_bw, center

    def trace_mode(self, mode='normal', channel=1):
        """
        modes:  -normal
                -max_hold
                -min_hold
                -average
        """
        if (mode == 'max_hold'):
            cmd = ':TRAC%i:MODE MAXH' % channel
        elif (mode == 'min_hold'):
            cmd = ':TRAC%i:MODE MINH' % channel
        elif (mode == 'average'):
            cmd = ':TRAC%i:MODE AVER' % channel
        else:
            cmd = ':TRAC%i:MODE WRIT' % channel
        self.instr.write(cmd)

    def set_instr_mode(self, mode='sa'):
        """
        modes:
                sa:     spectrum analyzer
                dma:    modulation analysis
                dtf:    distance to fault
                vna:    vector network analyzer
        """
        cmd = ':INST ' + str(mode)
        self.instr.write(cmd)

    def configure_vna(self, freq, pts):
        """
        Sets sva1075x in VNA mode and select the principal parameters.
        Note: The system must be calibrated.
        Parameters:
            freq:       [initial_freq, end_freq] in Hz
            res_bw:     resolution bw in Hz
            pts:        number of points
        """
        self.set_instr_mode('VNA')

        span = freq[1] - freq[0]
        central_freq = (freq[1] + freq[0]) / 2

        cmd = "FREQ:CENT %f Hz" %central_freq
        self.instr.write(cmd)
        time.sleep(self._sleep_time)

        cmd = "FREQ:SPAN %f Hz" % span
        self.instr.write(cmd)
        time.sleep(self._sleep_time)

        cmd = 'SWE:POIN %d' % pts
        self.instr.write(cmd)
        time.sleep(self._sleep_time)

        cmd = ':CALCulate1:PARameter1:DEFine S21'
        self.instr.write(cmd)
        time.sleep(self._sleep_time)


    def get_trace(self, channel=1):
        """
        Gets the current trace.
        Note: The system must be calibrated.
        Returns [frequencies, new_data]
            frequencies:    Sampled frequencies
            new_data:       Trace parameters in dB
        """
        data = self.instr.query_ascii_values(':TRAC:DATA? ' + str(channel), container = np.array)
        new_data = []
        frequencies = []
        for i in range(len(data)):
            if (i+1)%2 != 0:
                frequencies.append(data[i])
            else:
                new_data.append(data[i])

        return frequencies, new_data

    def plot_s11(self, freq, data, title):
        """
        Input
            freq:   (list) frequencies
            data:   (list) S11 parameters
            title:  (string) desired title
        """
        plt.title(title)
        plt.xlabel("Frequencies [Hz]")
        plt.ylabel("S11 [dB]")
        plt.plot(freq, data)
