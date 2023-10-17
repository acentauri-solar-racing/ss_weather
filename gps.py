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
    
    def __init__(self, com_port:str, baud:int=4800) -> None:
        self.position_df = pd.DataFrame()
        self.last_save_directory = ""

        self.ser = serial.Serial(com_port, baudrate=baud, timeout=5)

    @property
    def get_last_position(self) -> pd.DataFrame:
        """ """
        return self.position_df.tail(1)
    
    @property
    def get_all_positions(self) -> pd.DataFrame:
        """ """
        return self.position_df
    
    def get_current_location(self) -> dict:
        """ """
        i = 0
        found = False
        while not found and i < 30:
            # increasing i; if i < 30 --> no fix achieved
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
        
        now = pd.Timestamp.now(tz=constants.TIMEZONE)

        # Create a dataframe with the current location
        current_position = {
            'latitude': [latitude_dd],
            'longitude': [longitude_dd]
        }
        current_location_df = pd.DataFrame(current_position, index=[now])

        # Concatenate the current location dataframe with the position dataframe
        self.position_df = pd.concat([self.position_df, current_location_df])

        # Reset index
        self.position_df = self.position_df.reset_index(drop=True)

        return current_position
    
    def save_data2folder(self) -> None:
        """ """
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        root.lift()  # Bring the window to the front
        root.attributes('-topmost', True)  # Keep the window on top of all others
        
        chosen_directory = filedialog.askdirectory(
            initialdir=self.last_save_directory,
            title='Select a Folder to Append the GPS data to'
        )
        
        # If a directory is chosen
        if chosen_directory:
            # Check if the name of folder contains the current day
            pattern = os.path.join(chosen_directory, f"{self.CURRENT_DAY}_{self.SAVE_NAME}")
            directories_containing_current_day = [name for name in glob.glob(pattern) if os.path.isdir(name)]

            # If there is a folder containing the current day
            if directories_containing_current_day:
                print("A folder exists!")
                # Enter in the first folder
                first_folder = directories_containing_current_day[0]
                self.position_df.to_csv(os.path.join(first_folder, f"{self.CURRENT_DAY}_{self.SAVE_NAME}.csv"), mode='a', header=False, index=False)

            else:
                print("A folder does not exist!")
                # Create the new folder
                folder_name = f"{self.CURRENT_DAY}"
                new_folder_path = os.path.join(chosen_directory, folder_name)
                os.makedirs(new_folder_path)
                self.last_save_directory = new_folder_path # Update the last_save_directory attribute

                # Save the csv files
                self.position_df.to_csv(os.path.join(new_folder_path, f"{self.CURRENT_DAY}_{self.SAVE_NAME}.csv"), index=False)