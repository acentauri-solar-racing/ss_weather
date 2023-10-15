import pandas as pd
import os
import constants
import tkinter as tk
from tkinter import filedialog
from dateutil.tz import tzlocal

class OptReader():
    """ """
    
    def __init__(self, choose_specific_data:bool=True) -> None:
        self.previous_optimal_df: pd.DataFrame = self.read_optimal_data(choose_specific_data=choose_specific_data)
        self.previous_time: pd.Timestamp = pd.NaT

    @property
    def get_optimal_data(self) -> pd.DataFrame:
        """ Return the optimal data as a Pandas DataFrame. """
        return self.previous_optimal_df

    @property
    def get_optimal_last_time(self) -> pd.Timestamp:
        """ Return the time of the last optimal data. """
        return self.previous_time
    
    def read_optimal_data(self, choose_specific_data:bool=True) -> pd.DataFrame:
        """ """
        # Upload optimal data
        if choose_specific_data:
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            root.lift()  # Bring the window to the front
            root.attributes('-topmost', True)  # Keep the window on top of all others

            chosen_file = filedialog.askopenfilename(title='Select the csv file with optimal data', filetypes=[("CSV files", "*.csv")])

            if chosen_file:
                local_tz = tzlocal()
                self.previous_time = pd.Timestamp.now(tz=local_tz)
                self.previous_optimal_df = pd.read_csv(chosen_file)

                print(f"Data read from {chosen_file}.")
                return self.previous_optimal_df
            
            else:
                print("No directory chosen. Data not read.")
                return None
        
        # else:
        #     # Upload route data
        #     script_directory = os.path.dirname(os.path.abspath(__file__))
        #     csv_file_path = os.path.join(script_directory, constants.ROUTE)
        #     self.optimal_df = pd.read_csv(csv_file_path)