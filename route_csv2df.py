import pandas as pd
import os
import constants
import tkinter as tk
from tkinter import filedialog

class RouteDF():
    """ Import the route data from the csv file and generate a Pandas DataFrame. 
    
        Args:
            choose_specific_route (bool): If True, a file dialog will open to allow the user to choose a specific route file. 
                If False, the route file specified in constants.py will be used. Defaults to False. """
    
    def __init__(self, choose_specific_route:bool=False) -> None:
        self.control_stops_data = pd.DataFrame()

        if choose_specific_route:
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            root.lift()  # Bring the window to the front
            root.attributes('-topmost', True)  # Keep the window on top of all others

            chosen_file = filedialog.askopenfilename(title='Select the csv route file', filetypes=[("CSV files", "*.csv")])

            # If a file is chosen
            if chosen_file:
                self.route_data = pd.read_csv(chosen_file)
                print(f"Data read from {chosen_file}.")
            else:
                print("No directory chosen. Data not read.")
        
        else:
            # Get the path of the csv file saved in constants.py
            script_directory = os.path.dirname(os.path.abspath(__file__))
            csv_file_path = os.path.join(script_directory, constants.ROUTE)
            self.route_data = pd.read_csv(csv_file_path)

    @property
    def get_route_data(self) -> pd.DataFrame:
        """ Return the route data as a Pandas DataFrame. """
        return self.route_data
    
    @property
    def get_control_stops_data(self) -> pd.DataFrame:
        """ Return the control stop data as a Pandas DataFrame. """
        return self.control_stops_data
    
    def get_control_stops_csv2df(self, choose_specific_route:bool=False) -> pd.DataFrame:
        """ Return the control stop data as a Pandas DataFrame. """

        if choose_specific_route:
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            root.lift()  # Bring the window to the front
            root.attributes('-topmost', True)  # Keep the window on top of all others

            chosen_file = filedialog.askopenfilename(title='Select the csv file with control stops', filetypes=[("CSV files", "*.csv")])

            # If a file is chosen
            if chosen_file:
                self.route_data = pd.read_csv(chosen_file)
                print(f"Data read from {chosen_file}.")
            else:
                print("No directory chosen. Data not read.")
        
        else:
            # Get the path of the csv file saved in constants.py
            script_directory = os.path.dirname(os.path.abspath(__file__))
            csv_file_path = os.path.join(script_directory, constants.CONTROL_STOPS)
            self.control_stops_data = pd.read_csv(csv_file_path)