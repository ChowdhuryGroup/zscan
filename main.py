import oscilloscope
import stage_control
import matplotlib.pyplot as plt
import numpy as np

# Initialize Devices
keysight_oscope = oscilloscope.Oscilloscope('/opt/keysight/iolibs/libktvisa32.so')
keysight_oscope.select_channels((1,))

# model of VXM stage bi-slide E04, conversion factor btween steps and distance
# E04 = .0254 #mm/step
stage = stage_control.VXMController(step_size=0.0254)

# Step locations
positions = np.arange(1700, 3500, 10, dtype=int) #stage.max_index


# 3 Rows, 1 for each channel
average_voltage = np.zeros((3, len(positions)))
stdev_voltage = np.zeros((3, len(positions)))

keysight_oscope.set_signal_duration("500e-3")

# Loop through 3 photodiode signals
for j in range(1): #len(keysight_oscope.channels)):
    input('Plug in photodiode '+str(j+1)+', press Enter when ready to proceed...')

    # Loop through positions
    for i in range(len(positions)):
        # move stage to position
        stage.move_absolute(positions[i], 1000)

        # acquire signal for 1 second
        keysight_oscope.single_acquisition(1)
        keysight_oscope.process_data()
    
        avg = np.average(keysight_oscope.data[0])
        stdev = np.std(keysight_oscope.data[0])
        average_voltage[j,i] = avg
        stdev_voltage[j,i] = stdev
    
    stage.move_absolute(0, 1000)

del stage
del keysight_oscope

voltage_data = np.array(list(zip(positions, average_voltage[0,:], stdev_voltage[0,:], average_voltage[1,:], stdev_voltage[1,:], average_voltage[2,:], stdev_voltage[2,:])))
np.savetxt('raw_voltages.tsv', voltage_data, delimiter='\t')

plt.plot(positions, average_voltage[0,:], color='magenta', label='first')
plt.plot(positions, average_voltage[1,:], color='green', label='second')
plt.plot(positions, average_voltage[1,:] / average_voltage[0,:], color='orange', label='ratio')
plt.plot(positions, average_voltage[2,:], color='blue', label='third')
plt.legend()
plt.show()

#TODO: add live blitting plot


