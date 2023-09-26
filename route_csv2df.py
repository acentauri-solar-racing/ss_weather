import pandas as pd
import os
import constants
import tkinter as tk
from tkinter import filedialog

class RouteDF():
    """ Import the route data from the csv file and generate a Pandas DataFrame. """
    
    def __init__(self) -> None:
        script_directory = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_directory, constants.ROUTE)
        self.route_data = pd.read_csv(csv_file_path)

        # UNCOMMENT HERE TO GENERALIZE IT
        # root = tk.Tk()
        # root.withdraw()  # Hide the main window
        # root.lift()  # Bring the window to the front
        # root.attributes('-topmost', True)  # Keep the window on top of all others

        # chosen_file = filedialog.askopenfilename(title='Select the csv route file', filetypes=[("CSV files", "*.csv")])

        # # If a file is chosen
        # if chosen_file:
        #     self.route_data = pd.read_csv(chosen_file)
        #     print(f"Data read from {chosen_file}.")
        # else:
        #     print("No directory chosen. Data not read.")

    @property
    def get_route_data(self) -> pd.DataFrame:
        return self.route_data