import matplotlib.pyplot as plt
import numpy as np


fig, ax  = plt.subplots(figsize=(11,9))

artists = (ax.plot([], [], animated=True, color='golden')[0],
           ax.plot([], [], animated=True, color='green')[0],
           ax.plot([], [], animated=True, color='blue')[0])

# Shows the plot but doesn't stop the program
plt.show(block=False)
plt.pause(0.1)

# save a copy of the figure before filling it
background = fig.canvas.copy_from_bbox(fig.bbox)
for i in range(3):
    ax.draw_artist(artists[i])

fig.canvas.blit(fig.bbox)

for i in range(100):
    # Restore canvas to just background
    fig.canvas.restore_region(background)
    
    for j in range(3):
        artists[j].set_xdata()
        artists[j].set_ydata()
        ax.draw_artist(artists[j])
    
    # Copy image to GUI state, but may not show yet
    fig.canvas.blit(fig.bbox)

    # flush any pending GUI events, re-painting the screen if needed
    fig.canvas.flush_events()