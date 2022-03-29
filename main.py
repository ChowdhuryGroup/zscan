import oscilloscope
import stage_control
import matplotlib.pyplot as plt
import numpy as np

# Initialize Devices
keysight_oscope = oscilloscope.Oscilloscope('/opt/keysight/iolibs/libktvisa32.so')
keysight_oscope.select_channels((1,2,3))

# model of VXM stage bi-slide E04, conversion factor btween steps and distance
# E04 = .0254 #mm/step
stage = stage_control.VXMController(step_size=0.0254)

# Step locations
positions = np.arange(0, 4000, 1000, dtype=int)


# 3 Rows, 1 for each channel
average_voltage = np.ndarray((len(keysight_oscope.channels), len(positions)))
stdev_voltage = np.ndarray((len(keysight_oscope.channels), len(positions)))

for i in range(len(positions)):
    # move stage to position
    stage.move_absolute(positions[i], 1000)

    # acquire signal for 1 second
    keysight_oscope.single_acquisition(1)
    keysight_oscope.process_data()
    
    # Loop through 3 photodiode signals
    for j in range(len(keysight_oscope.channels)):
        avg = np.average(keysight_oscope.data[j])
        stdev = np.std(keysight_oscope.data[j])
        average_voltage[j,i] = avg
        stdev_voltage[j,i] = stdev

    voltages_string = 'PD1: {:.2E}\t'.format(average_voltage[0,i]) + \
                      'PD2: {:.2E}\t'.format(average_voltage[1,i]) + \
                      'PD3: {:.2E}\t'.format(average_voltage[2,i])
    print(voltages_string)

voltage_data = np.array(list(zip(positions, average_voltage[0,:], stdev_voltage[0,:], average_voltage[1,:], stdev_voltage[1,:], average_voltage[2,:], stdev_voltage[2,:])))
np.savetxt('raw_voltages.tsv', voltage_data, delimiter='\t')

plt.plot(positions, average_voltage[0,:], color='yellow')
plt.plot(positions, average_voltage[1,:], color='green')
plt.plot(positions, average_voltage[2,:], color='blue')
plt.show()


