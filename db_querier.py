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
    NUM_ENTRIES = 15
    MIN_VEL = 60 / 3.6 # in m/s

    CURRENT_DAY =  time.strftime('%Y%m%d')
    SAVE_NAME_SOC = 'SoC'
    SAVE_NAME_VELOCITY = 'Velocity'
    CSV_SOC = f"{CURRENT_DAY}_{SAVE_NAME_SOC}.csv"
    CSV_VELOCITY = f"{CURRENT_DAY}_{SAVE_NAME_VELOCITY}.csv"

    def __init__(self, gps:GPS, choose_specific:bool=False) -> None:
        # Add the can-msg-api folder to the path
        sys.path.append('C:/Users/giaco/Git_Repositories/aCentauri') #############TODO 
        sys.path.append('C:/Users/giaco/Git_Repositories/aCentauri/can-msg-api')

        can_db_service = importlib.import_module("can-msg-api.db.db_service")
        self.db_service = can_db_service.DbService(out_of_folder=True)

        self.can_db_models = importlib.import_module("can-msg-api.db.models")

        self.gps = gps

        if choose_specific:
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

                # Check and handle SoC CSV
                self._check_and_handle_csv(chosen_directory, self.SAVE_NAME_SOC, self.CSV_SOC, 'all_day_soc_df', 'save_directory_soc')

                # Check and handle Velocity CSV
                self._check_and_handle_csv(chosen_directory, self.SAVE_NAME_VELOCITY, self.CSV_VELOCITY, 'all_day_v_df', 'save_directory_velocity')
        else:
            dir = 'G:\\Drive condivisi\\AlphaCentauri\\SolarCar_22 23\\6. Strategy & Simulation\\ss_online_data\\Solar_car'
            self._check_and_handle_csv(dir, self.SAVE_NAME_SOC, self.CSV_SOC, 'all_day_soc_df', 'save_directory_soc')
            self._check_and_handle_csv(dir, self.SAVE_NAME_VELOCITY, self.CSV_VELOCITY, 'all_day_v_df', 'save_directory_velocity')
            
        self.new_data_day_soc_df = pd.DataFrame()
        self.new_data_day_v_df = pd.DataFrame()

    def _check_and_handle_csv(self, chosen_directory, save_name, csv_name, attribute_name, directory_name):
        # Check if the folder contains the specific CSV type (SoC or Velocity)
        pattern = os.path.join(chosen_directory, f"*{save_name}*")
        folder = [name for name in glob.glob(pattern) if os.path.isdir(name)]
        
        if folder:
            save_directory = folder[0]
            # Check if the folder contains the current day csv file
            pattern = os.path.join(save_directory, csv_name)
            csv_file = [name for name in glob.glob(pattern) if os.path.isfile(name)]

            if csv_file:
                # Extract data from csv file
                setattr(self, attribute_name, pd.read_csv(csv_file[0]))
            else:
                # Create the empty csv file
                df = pd.DataFrame(columns=['time', save_name, 'latitude', 'longitude'])
                df.to_csv(os.path.join(save_directory, csv_name), index=False)
                setattr(self, attribute_name, df)

        setattr(self, directory_name, save_directory)

    @property
    def get_day_mean_velocity(self) -> float:
        """ """
        return self.all_day_v_df['velocity'].mean()
    
    @property
    def get_day_mean_velocity60(self) -> float:
        """ """
        return self.all_day_v_df[self.all_day_v_df['velocity'] > self.MIN_VEL]['velocity'].mean()
    
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
        icu_time_series = icu_data['timestamp']

        # Convert the entire icu_time_series to a DatetimeIndex
        icu_datetime = pd.to_datetime(icu_time_series.mean(), unit='s').round('S')

        # Make it timezone aware
        icu_datetime_idx = pd.DatetimeIndex([icu_datetime]).tz_localize(constants.TIMEZONE)

        current_position = self.gps.get_current_location()

        # Create a DataFrame with the average values
        velocity_df = pd.DataFrame({
            'time': icu_datetime_idx,
            'velocity': icu_data['speed'].mean(),
            'latitude': current_position['latitude'],
            'longitude': current_position['longitude']
        })

        # Concatenate the average velocity
        self.all_day_v_df = pd.concat([self.all_day_v_df, velocity_df])
        self.new_data_day_v_df = pd.concat([self.new_data_day_v_df, velocity_df])

        return velocity_df
    
    def query_soc(self) -> pd.DataFrame:
        """ """
        # Query BmsPackSoc data
        bms_data = self.db_service.query_latest(orm_model=self.can_db_models.BmsPackSoc, num_entries=self.NUM_ENTRIES)
        bms_time_series = bms_data['timestamp']

        # Convert the entire time_series to a DatetimeIndex
        bms_datetime = pd.to_datetime(bms_time_series.mean(), unit='s').round('S')

        # Make it timezone aware
        bms_datetime_idx = pd.DatetimeIndex([bms_datetime]).tz_localize(constants.TIMEZONE)

        current_position = self.gps.get_current_location()

        soc_df = pd.DataFrame({'time': bms_datetime_idx,
                                'SoC': bms_data['soc_percent'].mean(),
                                'latitude': current_position['latitude'],
                                'longitude': current_position['longitude']})

        # Concatenate the current SoC
        self.all_day_soc_df = pd.concat([self.all_day_soc_df, soc_df])
        self.new_data_day_soc_df = pd.concat([self.new_data_day_soc_df, soc_df])

        return soc_df
    
    def save_data2folder(self) -> None:
        """ """
        self.new_data_day_soc_df.to_csv(os.path.join(self.save_directory_soc, self.CSV_SOC), mode='a', header=False, index=False)
        self.new_data_day_v_df.to_csv(os.path.join(self.save_directory_velocity, self.CSV_VELOCITY), mode='a', header=False, index=False)