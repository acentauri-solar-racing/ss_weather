# Created by Giacomo Mastroddi and Severin Meyer October 2023

import os
import time
import glob
import serial
import constants
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from route import Route

class GPS():
    """ Class to get the current location and save the data to a folder of the GPS. """
    CURRENT_DAY =  time.strftime('%Y%m%d')
    SAVE_NAME = 'GPS'
    
    def __init__(self, com_port:str, route:Route=None, baud:int=4800, choose_specific:bool=True) -> None:
        self.new_data_day_df = pd.DataFrame()
        self.ser = serial.Serial(com_port, baudrate=baud, timeout=5)
        self.route = route

        if choose_specific:
            self.last_save_directory = os.path.dirname(os.path.abspath(__file__))
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            root.lift()  # Bring the window to the front
            root.attributes('-topmost', True)  # Keep the window on top of all others
            
            chosen_directory = filedialog.askdirectory(title='Select the GPS Folder')

        else:
            chosen_directory = 'G:\\Shared drives\\AlphaCentauri\\SolarCar_22 23\\6. Strategy & Simulation\\ss_online_data\\Solar_car\\GPS'
        
        # If a directory is chosen
        if chosen_directory:
            self.last_save_directory = chosen_directory

            # Check if the folder contains the current day csv file
            pattern = os.path.join(chosen_directory, f"{self.CURRENT_DAY}_{self.SAVE_NAME}.csv")
            directories_containing_current_day = [name for name in glob.glob(pattern) if os.path.isfile(name)]
            
            # If there is one
            if directories_containing_current_day:
                # Extract data from csv file
                self.all_day_df = pd.read_csv(os.path.join(chosen_directory, f"{self.CURRENT_DAY}_{self.SAVE_NAME}.csv"))
                print("Data loaded from csv file")

            else:
                # Create the empty csv file
                self.all_day_df = pd.DataFrame(columns=['time', 'latitude', 'longitude', 'cumDistance'])
                self.all_day_df.to_csv(os.path.join(chosen_directory, f"{self.CURRENT_DAY}_{self.SAVE_NAME}.csv"), index=False)
                print("No csv file found. New created")

    @property
    def get_last_position(self) -> pd.DataFrame:
        """ Return the last position. """
        return self.all_day_df.tail(1)
    
    @property
    def get_all_positions(self) -> pd.DataFrame:
        """ Return all the positions of the day. """
        return self.all_day_df
    
    def get_current_location(self) -> dict:
        """ Return the current location as a dictionary. """
        i = 0
        found = False
        while not found and i < 30:
            # If i > 30: No fix achieved
            i += 1
            
            # Decode the bytes to a string using the correct encoding
            line = self.ser.readline().decode('ISO-8859-1') 
            splitline = line.split(',')
            
            # Getting GNGGA lines and checking if fix is active
            if (splitline[0] == '$GNGGA') and (splitline[6] != '0'): #if splitline[6] is 0, no GPS fix and invalid
                
                # Getting latitude/longitude DMM values
                latitude = float(splitline[2])
                longitude = float(splitline[4])
                
                # Getting latitude/longitude NSEW letters
                latitude_NS = splitline[3]
                longitude_EW = splitline[5]
                
                # DMM to DD conversion
                latitude_degrees = int(latitude) // 100  # Get the degrees part
                latitude_minutes = (latitude % 100) / 60  # Convert minutes to degrees
                latitude_dd = latitude_degrees + latitude_minutes
                longitude_degrees = int(longitude) // 100  # Get the degrees part
                longitude_minutes = (longitude % 100) / 60  # Convert minutes to degrees
                longitude_dd = longitude_degrees + longitude_minutes
                
                # Flipping signs for S and W coordinates
                if latitude_NS == 'S':
                    latitude_dd = -latitude_dd
                if longitude_EW == 'W':
                    longitude_dd = -longitude_dd
                
                # Output
                latitude_dd = round(latitude_dd, 6)
                longitude_dd = round(longitude_dd, 6)

                found = True

        if not found:
            print("No GPS fix achieved!")
            return None
        
        # Create a dataframe with the current location
        current_position = {
            'latitude': latitude_dd,
            'longitude': longitude_dd
        }

        # Add the cumulative distance if a route is given
        if self.route is not None:
            current_position['cumDistance'] = self.route.find_closest_row(current_position)[0]['cumDistance']

        current_location_df = pd.DataFrame({'time': [pd.Timestamp.now(tz=constants.TIMEZONE)], **current_position})

        # Concatenate the current location
        self.all_day_df = pd.concat([self.all_day_df, current_location_df])
        self.new_data_day_df = pd.concat([self.new_data_day_df, current_location_df])

        return current_position
    
    def save_data2folder(self) -> None:
        """ Save the new data to the folder and reset the new_data_df attribute. """
        self.new_data_day_df.to_csv(os.path.join(self.last_save_directory, f"{self.CURRENT_DAY}_{self.SAVE_NAME}.csv"), mode='a', header=False, index=False)
        self.new_data_day_df = pd.DataFrame() # Reset the new_data_df attribute