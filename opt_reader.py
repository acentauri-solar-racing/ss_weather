import pandas as pd
import os
import glob
import tkinter as tk
from tkinter import filedialog
from dateutil.tz import tzlocal

class OptReader():
    """ """
    
    def __init__(self, choose_specific:bool=True) -> None:
        _ = self.update_optimal_data(choose_specific=choose_specific)

    @property
    def get_optimal_data(self) -> pd.DataFrame:
        """ Return the optimal data as a Pandas DataFrame. """
        return self.optimal_df

    @property
    def get_optimal_last_time(self) -> pd.Timestamp:
        """ Return the time of the last optimal data. """
        return self.previous_time
    
    @property
    def get_mean_velocity(self) -> float:
        """ Return the mean velocity of the optimal data. """
        return self.optimal_df['velocity'].mean()
    
    def update_optimal_data(self, choose_specific:bool=True) -> pd.DataFrame:
        """ """
        # Upload optimal data
        if choose_specific:
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            root.lift()  # Bring the window to the front
            root.attributes('-topmost', True)  # Keep the window on top of all others

            chosen_file = filedialog.askopenfilename(title='Select the csv file with optimal data', filetypes=[("CSV files", "*.csv")])

            if chosen_file:
                local_tz = tzlocal()
                self.previous_time = pd.Timestamp.now(tz=local_tz)

                self.optimal_df = pd.read_csv(chosen_file)
                print(f"Data read from {chosen_file}.")
            
            else:

                self.optimal_df = pd.DataFrame()
                self.previous_time: pd.Timestamp = pd.NaT
                print("No directory chosen. Data not read.")
        
        else:
            script_directory = 'G:\\Shared drives\\AlphaCentauri\\SolarCar_22 23\\6. Strategy & Simulation\\ss_online_data\\DP_optimal'

            # Check in the folder for the most recent csv file
            pattern = os.path.join(script_directory, "*.csv")
            list_of_files = glob.glob(pattern)

            if list_of_files:
                local_tz = tzlocal()
                self.previous_time = pd.Timestamp.now(tz=local_tz)

                latest_file = max(list_of_files, key=os.path.getctime)
                self.optimal_df = pd.read_csv(latest_file)
                print(f"Data read from {latest_file}.")
            else:

                self.optimal_df = pd.DataFrame()
                self.previous_time: pd.Timestamp = pd.NaT
                print("No csv file found in the folder!")