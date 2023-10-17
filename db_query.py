import importlib
import os
import sys
import glob
import time
import constants
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from gps import GPS

class DbQuerier():
    """ Class to query the database and save the data to a folder."""
    NUM_ENTRIES = 5
    CURRENT_DAY =  time.strftime('%Y%m%d')
    SAVE_NAME_SOC = 'SoC'
    SAVE_NAME_VELOCITY = 'v'

    def __init__(self, gps:GPS) -> None:
        sys.path.append('C:/Users/giaco/Git_Repositories/aCentauri') #############TODO 
        sys.path.append('C:/Users/giaco/Git_Repositories/aCentauri/can-msg-api')

        can_db_service = importlib.import_module("can-msg-api.db.db_service")
        self.db_service = can_db_service.DbService(out_of_folder=True)

        self.can_db_models = importlib.import_module("can-msg-api.db.models")

        self.last_velocity_df: pd.DataFrame()
        self.last_soc_df: pd.DataFrame()

        self.last_save_directory = os.path.dirname(os.path.abspath(__file__))

        self.gps = gps

    @property
    def get_day_mean_velocity(self) -> float:
        """ """
        return self.last_velocity_df['velocity'].mean()

    def query_velocity(self) -> pd.DataFrame:
        """ """
        # Query IcuHeartbeat data
        icu_data = self.db_service.query_latest(orm_model=self.can_db_models.IcuHeartbeat, num_entries=self.NUM_ENTRIES)
        velocity = icu_data['speed']
        icu_time_series = icu_data['timestamp']

        # Convert the entire icu_time_series to a DatetimeIndex
        icu_datetimes = pd.to_datetime(icu_time_series, unit='s').round('S')

        # Make it timezone aware
        icu_datetimes_idx = pd.DatetimeIndex(icu_datetimes).tz_localize(constants.TIMEZONE)

        current_position = self.gps.get_current_location()

        self.last_velocity_df = pd.DataFrame({'velocity': velocity.values,
                                              'latitude': current_position['latitude'],
                                              'longitude': current_position['longitude']}, index=icu_datetimes_idx)

        return self.last_velocity_df
    
    def query_soc(self) -> pd.DataFrame:
        """ """
        # Query BmsPackSoc data
        bms_data = self.db_service.query_latest(orm_model=self.can_db_models.BmsPackSoc, num_entries=self.NUM_ENTRIES)
        soc = bms_data['soc_percent']
        bms_time_series = bms_data['timestamp']

        # Convert the entire time_series to a DatetimeIndex
        bms_datetimes = pd.to_datetime(bms_time_series, unit='s').round('S')

        # Make it timezone aware
        bms_datetimes_idx = pd.DatetimeIndex(bms_datetimes).tz_localize(constants.TIMEZONE)

        current_position = self.gps.get_current_location()

        self.last_soc_df = pd.DataFrame({'SoC': soc.values,
                                         'latitude': current_position['latitude'],
                                         'longitude': current_position['longitude']}, index=bms_datetimes_idx)

        return self.last_soc_df
    
    def save_data2folder(self) -> None:
        """ """
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        root.lift()  # Bring the window to the front
        root.attributes('-topmost', True)  # Keep the window on top of all others
        
        chosen_directory = filedialog.askdirectory(
            initialdir=self.last_save_directory,
            title='Select a Folder to Append the Velocity and SoC Data to'
        )
        
        # If a directory is chosen
        if chosen_directory:
            # Check if the name of folder contains the current day
            pattern = os.path.join(chosen_directory, f"*{self.CURRENT_DAY}*")
            directories_containing_current_day = [name for name in glob.glob(pattern) if os.path.isdir(name)]

            # If there is a folder containing the current day
            if directories_containing_current_day:
                print("A folder exists!")
                # Enter in the first folder
                first_folder = directories_containing_current_day[0]

                # Check if the name of csv files inside contains SoC and v
                pattern = os.path.join(first_folder, f"*{self.SAVE_NAME_SOC}*.csv")
                soc_files = [name for name in glob.glob(pattern) if os.path.isfile(name)]

                pattern = os.path.join(first_folder, f"*{self.SAVE_NAME_VELOCITY}*.csv")
                velocity_files = [name for name in glob.glob(pattern) if os.path.isfile(name)]

                # If there are both SoC and v files
                if soc_files and velocity_files:
                    # Append new data to existing CSV file
                    self.last_soc_df.to_csv(os.path.join(first_folder, f'{self.SAVE_NAME_SOC}.csv'), mode='a', header=False, index=False)
                    self.last_velocity_df.to_csv(os.path.join(first_folder, f'{self.SAVE_NAME_VELOCITY}.csv'), mode='a', header=False, index=False)
                
                # If there are only SoC files
                elif soc_files:
                    # Append new data to existing CSV file
                    self.last_soc_df.to_csv(os.path.join(first_folder, f'{self.SAVE_NAME_SOC}.csv'), mode='a', header=False, index=False)
                    self.last_velocity_df.to_csv(os.path.join(first_folder, f'{self.SAVE_NAME_VELOCITY}.csv'), index=False)

                # If there are only v files
                elif velocity_files:
                    # Append new data to existing CSV file
                    self.last_soc_df.to_csv(os.path.join(first_folder, f'{self.SAVE_NAME_SOC}.csv'), index=False)
                    self.last_velocity_df.to_csv(os.path.join(first_folder, f'{self.SAVE_NAME_VELOCITY}.csv'), mode='a', header=False, index=False)

            else:
                print("A folder does not exist!")
                # Create the new folder
                folder_name = f"{self.CURRENT_DAY}"
                new_folder_path = os.path.join(chosen_directory, folder_name)
                os.makedirs(new_folder_path)
                self.last_save_directory = new_folder_path # Update the last_save_directory attribute

                # Save the csv files
                self.last_soc_df.to_csv(os.path.join(new_folder_path, f'{self.SAVE_NAME_SOC}.csv'), index=False)

                self.last_velocity_df.to_csv(os.path.join(new_folder_path, f'{self.SAVE_NAME_VELOCITY}.csv'), index=False)