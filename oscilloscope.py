import pyvisa
import numpy as np
import matplotlib.pyplot as plt
import time


class Oscilloscope:

    def __init__(self, visa_library_binary_location: str) -> None:
        self.rm = pyvisa.ResourceManager(visa_library_binary_location) #'/opt/keysight/iolibs/libktvisa32.so')
        inst_list = self.rm.list_resources()
        print('Instrument list:')
        print(inst_list)
        index = input('Select instrument by typing index\n')
        self.inst = self.rm.open_resource(inst_list[int(index)])

        print('ID of connected instrument')
        print(self.inst.query('*IDN?'))

        # I think this gives the maximum number of data points...
        self.inst.write(':WAVeform:POINts:MODE MAX')

        # Set output format
        self.inst.write(":WAVeform:FORMat WORD") # 16 bit WORD format... or BYTE for 8 bit format
        self.inst.write(":WAVeform:UNSigned 0") # Set signed integer
        self.inst.write(":WAVeform:BYTeorder LSBFirst") # Most computers use Least Significant Bit First

        self.raw_data = []
        self.data = []


    def select_channels(self, channels: tuple):
        self.channels = channels
        for i in range(1,5):
            self.inst.write(':CHANnel'+str(i)+':DISPlay OFF')
        for i in channels:
            self.inst.write(':CHANnel'+str(i)+':DISPlay ON')


    def get_preamble(self):
        # Get waveform preamble
        '''
        FORMAT: int16 - 0 = BYTE, 1 = WORD, 4 = ASCII.
        TYPE: int16 - 0 = NORMAL, 1 = PEAK DETECT, 2 = AVERAGE
        POINTS: int32 - number of data points transferred.
        COUNT: int32 - 1 and is always 1.
        XINCREMENT: float64 - time difference between data points.
        XORIGIN: float64 - always the first data point in memory.
        XREFERENCE: int32 - specifies the data point associated with x-origin.
        YINCREMENT: float32 - voltage diff between data points.
        YORIGIN: float32 - value is the voltage at center screen.
        YREFERENCE: int32 - specifies the data point where y-origin occurs.
        '''
        preamble_keys = ['format',
                        'type',
                        'points',
                        'count',
                        'xincrement',
                        'xorigin',
                        'xreference',
                        'yincrement',
                        'yorigin',
                        'yreference']
        
        preamble_data = self.inst.query(':WAVeform:PREamble?').split(',')
        preamble_data[-1] = preamble_data[-1][:-1]
        self.preamble = dict(zip(preamble_keys, preamble_data))
        print(self.preamble)


    def set_signal_duration(self, duration: float):
        # Set signal duration (maximum 500s)
        self.inst.write(':TIMebase:RANGe '+str(duration))
    

    def single_acquisition(self, duration: float):
        self.set_signal_duration(duration)
        # Start a single acquisition
        self.inst.write(':SINGle')
        time.sleep(duration+1)

        self.raw_data = []
        for channel in self.channels:
            # h is signed WORD, H is unsigned WORD
            self.raw_data.append(self.inst.query_binary_values(':WAVeform:SOURce CHANnel'+str(channel)+';DATA?', container=np.array, datatype='h', is_big_endian=False))

    def process_data(self):
        # Calculate time values from preamble
        self.times = (np.arange(0,int(self.preamble['points'])) - int(self.preamble['xreference']))*float(self.preamble['xincrement']) + float(self.preamble['xorigin'])


        # Transform binary IEEE 488.2 data to actual values
        def binary_to_float(data):
            return ((data - int(self.preamble['yreference'])) * float(self.preamble['yincrement'])) + float(self.preamble['yorigin'])

        '''
        IEEE 488.2 Data types
        NR1: Signed integer
        NR2: Float with no exponent (not used by HP)
        NR3: Float always with exponent
        '''
        self.data = []
        for i in range(len(self.channels)):
            self.data.append(binary_to_float(self.raw_data[i]))
        

    def plot_data(self):
        # Plot the data
        for i in range(len(self.channels)):
            plt.plot(self.times, self.data[i], label='channel '+str(self.channels[i]), alpha=0.5)
        plt.legend()
        plt.show()
