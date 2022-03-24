import oscilloscope
import stage_control
import matplotlib.pyplot as plt
import numpy as np

keysight_oscope = oscilloscope.Oscilloscope('C:/Program Files/IVI Foundation/VISA/Win64/ktvisa/lib/msc/visa32.lib')

positions = np.linspace(-10, 10, 100, endpoint=True)
print(positions)

# 3 Rows, 1 for each channel
average_voltage = np.array((3, len(positions)))
stdev_voltage = np.array((3, len(positions)))

for i in range(len(positions)):
    print(positions[i])
    # move stage to position

    # acquire signal for 1 second
    keysight_oscope.single_acquisition(1)
    keysight_oscope.process_data()
    
    # Loop through 3 photodiode signals
    for j in range(3):
        avg = np.average(keysight_oscope.data[j])
        stdev = np.std(keysight_oscope.data[j])
        average_voltage[j,i] = avg
        stdev_voltage[j,i] = stdev

voltage_data = np.array(zip(positions, average_voltage[0,:], stdev_voltage[0,:], average_voltage[1,:], stdev_voltage[1,:], average_voltage[2,:], stdev_voltage[2,:]))
np.savetxt('raw_voltages.tsv', voltage_data, delimiter='\t')

plt.plot(positions, average_voltage)
plt.show()