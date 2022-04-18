import matplotlib.pyplot as plt
import numpy as np


class LivePlot():

    def __init__(self):
        self.fig, self.ax  = plt.subplots(figsize=(8,5))

        self.ax.set_ylim(0., 2.)
        self.ax.set_xlim(0., 100.)

        self.artists = (self.ax.plot([], [], color='gold')[0],
                        self.ax.plot([], [], color='green')[0],
                        self.ax.plot([], [], color='blue')[0])

        # Shows the plot but doesn't stop the program
        plt.show(block=False)
            
        # Save a copy of the figure before filling it
        plt.pause(0.1)
        self.background = self.fig.canvas.copy_from_bbox(self.fig.bbox)

        for i in range(len(self.artists)):
            self.artists[i].set_xdata(np.arange(100))
            self.artists[i].set_ydata(np.ones(100))

        # Copy image to GUI state, but may not show yet
        self.fig.canvas.draw()
        # Flush any pending GUI events, paint the window
        self.fig.canvas.flush_events()
        


    def update(self, x_vals, data):
        '''
        Update the plot data and then redraw the lines
        '''

        # Restore canvas to just background
        self.fig.canvas.restore_region(self.background)

        for i in range(len(self.artists)):
            self.artists[i].set_data(x_vals, data[i,:])
            self.ax.draw_artist(self.artists[i])
        
        # Copy image to GUI state, but may not show yet
        self.fig.canvas.blit(self.fig.bbox)

        # flush any pending GUI events, re-painting the screen if needed
        self.fig.canvas.flush_events()


test = LivePlot()
import time

x = np.linspace(0, 100, 1000)
test_data = [[0.],[0.],[0.]]
for p in range(100):
    test_data[0,:] = np.cos(x-0.05*p)+1
    test_data[1,:] = np.cos(x-0.10*p)+1
    test_data[2,:] = np.cos(x-0.15*p)+1
    test.update(x, test_data)

    time.sleep(0.1)