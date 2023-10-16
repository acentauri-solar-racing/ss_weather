import os
import serial
import constants
import pandas as pd
import tkinter as tk
from tkinter import filedialog

class GPS():
    """ Explanation """
    
    def __init__(self, com_port:str, baud:int=9600) -> None:
        self.previous_position = pd.DataFrame()

        self.ser = serial.Serial(com_port, baudrate=baud, timeout=1)
    
    # _private method
    def _parse_output(self, output) -> pd.DataFrame:
        """ """
        pass
    
    def get_current_location(self) -> pd.DataFrame:
        """ """
        output = self.ser.readline() # ...

        data = self._parse_output(output)

        now = pd.Timestamp.now(tz=constants.TIMEZONE)
        # insert also data
        current_location_df = pd.DataFrame(columns=['latitude', 'longitude', 'velocity'], index=now)

        return current_location_df
    
    # Can use something like this to save the data to a folder
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
                print(pattern)

                pattern = os.path.join(first_folder, f"*{self.SAVE_NAME_VELOCITY}*.csv")
                print(pattern)
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