import matplotlib.pyplot as plt
import numpy as np


class LivePlot():

    def __init__(self):
        self.fig, self.ax  = plt.subplots(figsize=(11,9))

        self.ax.set_ylim(0., 2.)
        self.ax.set_xlim(0., 100.)

        self.artists = (self.ax.plot([], [], animated=True, color='gold')[0],
                        self.ax.plot([], [], animated=True, color='green')[0],
                        self.ax.plot([], [], animated=True, color='blue')[0])

        # Shows the plot but doesn't stop the program
        plt.show(block=False)
            
        # Save a copy of the figure before filling it
        plt.pause(0.1)
        self.background = self.fig.canvas.copy_from_bbox(self.fig.bbox)

        for i in range(len(self.artists)):
            self.artists[i].set_data(np.zeros(100), np.zeros(100))
            self.ax.draw_artist(self.artists[i])

        # Copy image to GUI state, but may not show yet
        self.fig.canvas.blit(self.fig.bbox)
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
        #self.fig.canvas.blit(self.fig.bbox)
        self.fig.draw()

        # flush any pending GUI events, re-painting the screen if needed
        self.fig.canvas.flush_events()


test = LivePlot()

test.update(np.arange(0,100,1), np.ones((3,100)))
input()