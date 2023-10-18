import os
import time
import glob
import serial
import constants
import pandas as pd
import tkinter as tk
from tkinter import filedialog

class GPS():
    """ Explanation """
    CURRENT_DAY =  time.strftime('%Y%m%d')
    SAVE_NAME = 'GPS'
    
    def __init__(self, com_port:str, baud:int=4800, choose_specific:bool=False) -> None:

        if choose_specific:
            self.last_save_directory = os.path.dirname(os.path.abspath(__file__))

        else:
            self.last_save_directory = 'G:\\Drive condivisi\\AlphaCentauri\\SolarCar_22 23\\6. Strategy & Simulation\\ss_online_data\\Solar_car\\GPS'
            
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        root.lift()  # Bring the window to the front
        root.attributes('-topmost', True)  # Keep the window on top of all others
        
        chosen_directory = filedialog.askdirectory(
            initialdir=self.last_save_directory,
            title='Select the GPS Folder'
        )
        
        # If a directory is chosen
        if chosen_directory:
            self.last_save_directory = chosen_directory

            # Check if the folder contains the current day csv file
            pattern = os.path.join(chosen_directory, f"{self.CURRENT_DAY}_{self.SAVE_NAME}.csv")
            directories_containing_current_day = [name for name in glob.glob(pattern) if os.path.isfile(name)]
            
            # If there is one
            if directories_containing_current_day:
                # Extract data from csv file
                self.all_day_df = pd.read_csv(f"{self.CURRENT_DAY}_{self.SAVE_NAME}.csv")

            else:
                print("No csv file found for the current day!")
                # Create the empty csv file
                self.all_day_df = pd.DataFrame(columns=['time', 'latitude', 'longitude'])
                print(self.all_day_df)
                self.all_day_df.to_csv(os.path.join(chosen_directory, f"{self.CURRENT_DAY}_{self.SAVE_NAME}.csv"), index=False)
        
        self.new_data_day_df = pd.DataFrame()

        self.ser = serial.Serial(com_port, baudrate=baud, timeout=5)

    @property
    def get_last_position(self) -> pd.DataFrame:
        """ """
        return self.all_day_df.tail(1)
    
    @property
    def get_all_positions(self) -> pd.DataFrame:
        """ """
        return self.all_day_df
    
    def get_current_location(self) -> dict:
        """ """
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

        current_location_df = pd.DataFrame({'time': [pd.Timestamp.now(tz=constants.TIMEZONE)], **current_position})

        # Concatenate the current location
        self.all_day_df = pd.concat([self.all_day_df, current_location_df])
        self.new_data_day_df = pd.concat([self.new_data_day_df, current_location_df])

        return current_position
    
    def save_data2folder(self) -> None:
        """ """
        self.new_data_day_df.to_csv(os.path.join(self.last_save_directory, f"{self.CURRENT_DAY}_{self.SAVE_NAME}.csv"), mode='a', header=False, index=False)
        self.new_data_day_df = pd.DataFrame() # Reset the new_data_df attribute