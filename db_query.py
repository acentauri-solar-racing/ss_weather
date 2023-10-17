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
    SAVE_NAME_VELOCITY = 'Velocity'
    CSV_SOC = f"{CURRENT_DAY}_{SAVE_NAME_SOC}.csv"
    CSV_VELOCITY = f"{CURRENT_DAY}_{SAVE_NAME_VELOCITY}.csv"

    def __init__(self, gps:GPS) -> None:
        # Add the can-msg-api folder to the path
        sys.path.append('C:/Users/giaco/Git_Repositories/aCentauri') #############TODO 
        sys.path.append('C:/Users/giaco/Git_Repositories/aCentauri/can-msg-api')

        can_db_service = importlib.import_module("can-msg-api.db.db_service")
        self.db_service = can_db_service.DbService(out_of_folder=True)

        self.can_db_models = importlib.import_module("can-msg-api.db.models")

        # Open old data
        self.last_save_directory = os.path.dirname(os.path.abspath(__file__))

        root = tk.Tk()
        root.withdraw()  # Hide the main window
        root.lift()  # Bring the window to the front
        root.attributes('-topmost', True)  # Keep the window on top of all others
        
        # Ask the user to select TWO folders containing the data
        chosen_directory = filedialog.askdirectory(
            initialdir=self.last_save_directory,
            title='Select the Solar_car Folder'
        )
        
        # If a directory is chosen
        if chosen_directory:
            self.last_save_directory = chosen_directory

            # Check if the folder contains Soc
            pattern = os.path.join(chosen_directory, f"*{self.SAVE_NAME_SOC}*")
            soc_folder = [name for name in glob.glob(pattern) if os.path.isdir(name)]

            # Assuming the SoC folder exists
            if soc_folder:
                # Check if the folder contains the current day csv file
                pattern = os.path.join(soc_folder[0], self.CSV_SOC)
                soc_file = [name for name in glob.glob(pattern) if os.path.isfile(name)]

                if soc_file:
                    # Extract data from csv file
                    self.all_day_soc_df = pd.read_csv(soc_file[0])

                else:
                    # Create the empty csv file
                    self.all_day_soc_df = pd.DataFrame()
                    self.all_day_soc_df.to_csv(self.CSV_SOC, index=False)

            # Check if the folder contains Velocity
            pattern = os.path.join(chosen_directory, f"*{self.SAVE_NAME_VELOCITY}*")
            velocity_folder = [name for name in glob.glob(pattern) if os.path.isdir(name)]

            # Assuming the Velocity folder exists
            if velocity_folder:
                # Check if the folder contains the current day csv file
                pattern = os.path.join(velocity_folder[0], self.CSV_VELOCITY)
                velocity_file = [name for name in glob.glob(pattern) if os.path.isfile(name)]

                if velocity_file:
                    # Extract data from csv file
                    self.all_day_v_df = pd.read_csv(velocity_file[0])

                else:
                    self.all_day_v_df = pd.DataFrame()
                    self.all_day_v_df.to_csv(self.CSV_VELOCITY, index=False)
        
        self.new_data_day_soc_df = pd.DataFrame()
        self.new_data_day_v_df = pd.DataFrame()

        self.gps = gps

    @property
    def get_day_mean_velocity(self) -> float:
        """ """
        return self.all_day_v_df['velocity'].mean()
    
    @property
    def get_last_velocity(self) -> float:
        """ """
        return self.all_day_v_df['velocity'].tail(1)
    
    @property
    def get_last_soc(self) -> float:
        """ """
        return self.all_day_soc_df['SoC'].tail(1)

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

        velocity_df = pd.DataFrame({'time': icu_datetimes_idx,
                                    'velocity': velocity.values,
                                    'latitude': current_position['latitude'],
                                    'longitude': current_position['longitude']})
        
        # Concatenate the current velocity
        self.all_day_v_df = pd.concat([self.all_day_v_df, velocity_df])
        self.new_data_day_v_df = pd.concat([self.new_data_day_v_df, velocity_df])

        return velocity_df
    
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

        soc_df = pd.DataFrame({'time': bms_datetimes_idx,
                                    'SoC': soc.values,
                                    'latitude': current_position['latitude'],
                                    'longitude': current_position['longitude']})

        # Concatenate the current SoC
        self.all_day_soc_df = pd.concat([self.all_day_soc_df, soc_df])
        self.new_data_day_soc_df = pd.concat([self.new_data_day_soc_df, soc_df])

        return soc_df
    
    def save_data2folder(self) -> None:
        """ """
        self.new_data_day_soc_df.to_csv(os.path.join(self.last_save_directory, self.CSV_SOC), mode='a', header=False, index=False)
        self.new_data_day_v_df.to_csv(os.path.join(self.last_save_directory, self.CSV_VELOCITY), mode='a', header=False, index=False)