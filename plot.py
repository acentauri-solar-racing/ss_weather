import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

data1 = [
    [0, 1, 2, 3, 4],
    [0, 1.1, 2.1, 3.1, 4.1],
    [0, 1.2, 2.2, 3.2, 4.2],
    [0, 1.3, 2.3, 3.3, 4.3],
    [0, 1.4, 2.4, 3.4, 4.4]
]

data2 = [
    [0, 2, 4, 6, 8],
    [0, 2.2, 4.2, 6.2, 8.2],
    [0, 2.4, 4.4, 6.4, 8.4],
    [0, 2.6, 4.6, 6.6, 8.6],
    [0, 2.8, 4.8, 6.8, 8.8]
]

data1 = np.array(data1)
data2 = np.array(data2)

times = data1[:, 0]
distances1 = data1[0, :]
distances2 = data2[0, :]

# Create the main plotting figure and axis
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, sharey=True)
plt.subplots_adjust(bottom=0.25, hspace=0.4)

# Initial plots
line1, = ax1.plot(distances1, data1[0, :], 'r-')
line2, = ax2.plot(distances2, data2[0, :], 'b-')

# Set limits
max_distance = max(max(distances1), max(distances2))
max_value = max(np.max(data1), np.max(data2))

ax1.set_xlim(0, max_distance)
ax1.set_ylim(0, max_value)
ax2.set_xlim(0, max_distance)
ax2.set_ylim(0, max_value)

# Add a slider for time
ax_slider = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
slider = Slider(ax_slider, 'Time', 0, len(times) - 1, valinit=0, valstep=1)

# Update function for the slider
def update(val):
    time_idx = int(slider.val)
    line1.set_ydata(data1[time_idx, :])
    line2.set_ydata(data2[time_idx, :])
    fig.canvas.draw_idle()

slider.on_changed(update)

plt.show()
