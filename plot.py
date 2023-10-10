# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.widgets import Slider
# import os
# import pandas as pd
# import tkinter as tk
# from tkinter import filedialog
# import math

# root = tk.Tk()
# root.withdraw()  # Hide the main window
# root.lift()  # Bring the window to the front
# root.attributes('-topmost', True)  # Keep the window on top of all others

# chosen_directory = filedialog.askdirectory(title='Select the directory containing CSV files')

# dataframes = {}  # Dictionary to store dataframes

# if chosen_directory:
#     # List all CSV files in the chosen directory
#     csv_files = [f for f in os.listdir(chosen_directory) if f.endswith('.csv')]
    
#     for csv_file in csv_files:
#         file_path = os.path.join(chosen_directory, csv_file)
#         csv_file = str(csv_file).replace('.csv', '')
#         dataframes[csv_file] = pd.read_csv(file_path)
#         # print(f"Data read from {file_path}.")
# else:
#     print("No directory chosen. Data not read.")

# # Extract the time values for the slider
# times = dataframes['temperature']['time'].values

# # Create subplots for each CSV file
# fig, axes = plt.subplots(len(dataframes), 1, sharex=True, figsize=(10, 6))
# plt.subplots_adjust(bottom=0.25, hspace=0.4)

# # Adjust x-values
# x_values = [math.ceil(float(x)/1000) for x in dataframes['temperature'].columns[1:]]

# # Initial plots
# for ax, (key, df) in zip(axes, dataframes.items()):
#     line, = ax.plot(x_values, df.iloc[0, 1:].values, label=key)
#     ax.set_title(key)
#     ax.set_ylabel('Values')

# # Add a slider for time
# ax_slider = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
# slider = Slider(ax_slider, 'Time', 0, len(times) - 1, valinit=0, valstep=1, valfmt='%d')

# # Update function for the slider
# def update(val):
#     time_idx = int(slider.val)
#     for ax, (key, df) in zip(axes, dataframes.items()):
#         ax.lines[0].set_ydata(df.iloc[time_idx, 1:].values)
#     fig.canvas.draw_idle()

# slider.on_changed(update)

# # Function to synchronize x-axis zoom across all subplots
# def on_xlims_change(event_ax):
#     xlim = event_ax.get_xlim()
#     for ax in axes:
#         ax.set_xlim(xlim)

# for ax in axes:
#     ax.callbacks.connect("xlim_changed", on_xlims_change)

# plt.tight_layout()
# plt.show()



# #############################3333

# # import numpy as np
# # import matplotlib.pyplot as plt
# # from matplotlib.widgets import Slider

# # data1 = [
# #     [0, 1, 2, 3, 4],
# #     [0, 1.1, 2.1, 3.1, 4.1],
# #     [0, 1.2, 2.2, 3.2, 4.2],
# #     [0, 1.3, 2.3, 3.3, 4.3],
# #     [0, 1.4, 2.4, 3.4, 4.4]
# # ]

# # data2 = [
# #     [0, 2, 4, 6, 8],
# #     [0, 2.2, 4.2, 6.2, 8.2],
# #     [0, 2.4, 4.4, 6.4, 8.4],
# #     [0, 2.6, 4.6, 6.6, 8.6],
# #     [0, 2.8, 4.8, 6.8, 8.8]
# # ]

# # data1 = np.array(data1)
# # data2 = np.array(data2)

# # times = data1[:, 0]
# # distances1 = data1[0, :]
# # distances2 = data2[0, :]

# # # Create the main plotting figure and axis
# # fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, sharey=True)
# # plt.subplots_adjust(bottom=0.25, hspace=0.4)

# # # Initial plots
# # line1, = ax1.plot(distances1, data1[0, :], 'r-')
# # line2, = ax2.plot(distances2, data2[0, :], 'b-')

# # # Set limits
# # max_distance = max(max(distances1), max(distances2))
# # max_value = max(np.max(data1), np.max(data2))

# # ax1.set_xlim(0, max_distance)
# # ax1.set_ylim(0, max_value)
# # ax2.set_xlim(0, max_distance)
# # ax2.set_ylim(0, max_value)

# # # Add a slider for time
# # ax_slider = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
# # slider = Slider(ax_slider, 'Time', 0, len(times) - 1, valinit=0, valstep=1)

# # # Update function for the slider
# # def update(val):
# #     time_idx = int(slider.val)
# #     line1.set_ydata(data1[time_idx, :])
# #     line2.set_ydata(data2[time_idx, :])
# #     fig.canvas.draw_idle()

# # slider.on_changed(update)

# # plt.show()

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import math

# Prompt user to select a CSV file
root = tk.Tk()
root.withdraw()  # Hide the main window
root.lift()  # Bring the window to the front
root.attributes('-topmost', True)  # Keep the window on top of all others

chosen_file = filedialog.askopenfilename(title='Select the csv file', filetypes=[("CSV files", "*.csv")])

if not chosen_file:
    print("No file chosen. Exiting.")
    exit()

# Load the selected CSV file into a DataFrame
df = pd.read_csv(chosen_file)

# Extract the time values for the slider
times = df['time'].values

# Create the main plotting figure and axis
fig, ax = plt.subplots(figsize=(10, 6))
plt.subplots_adjust(bottom=0.25)

# Adjust x-values
x_values = [math.ceil(float(x)/1000) for x in df.columns[1:]]

# Initial plot
line, = ax.plot(x_values, df.iloc[0, 1:].values)

# Set y-axis limits to the minimum and maximum values of the data
ax.set_ylim(df.iloc[:, 1:].min().min(), df.iloc[:, 1:].max().max())

# Turn on the grid
ax.grid(True)

# Add a slider for time
ax_slider = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
slider = Slider(ax_slider, 'Time', 0, len(times) - 1, valinit=0, valstep=1, valfmt='%d')

# Update function for the slider
def update(val):
    time_idx = int(slider.val)
    line.set_ydata(df.iloc[time_idx, 1:].values)
    fig.canvas.draw_idle()

slider.on_changed(update)

plt.tight_layout()
plt.show()
