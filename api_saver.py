import os
import time
import pandas as pd
import tkinter as tk
from tkinter import filedialog

class ApiSaver():
    """
    TODO
    """

    def __init__(self) -> None:
        self.last_save_directory:str = ''

    def _data_restructure(self, route_df:pd.DataFrame, sites_df:pd.DataFrame, forecast_df:pd.DataFrame) -> pd.DataFrame:
        """
        TODO
        """
        # Given a site_id from forecast_df, find the corresponding name from sites_df, find the cumDistance from route_df
        index_forecast = forecast_df.index.get_level_values('site_id').unique()
        index_sites = sites_df.index

        # Check that the indices are the same
        if not index_forecast.equals(index_sites):
            raise ValueError('The index of the forecast dataframe and the sites dataframe are not the same')

        # Merge forecast_df with sites_df on site_id to get the name
        merged_df = forecast_df.reset_index().merge(sites_df[['name']], left_on='site_id', right_index=True)

        # Convert the name column to int64
        merged_df['name'] = merged_df['name'].astype('int64')

        # Merge the result with route_df on name to get cumDistance
        merged_df = merged_df.merge(route_df[['cumDistance']], left_on='name', right_index=True)

        # Set the index to cumDistance and time
        merged_df.set_index(['cumDistance', 'time'], inplace=True)

        # Drop the site_id and name columns as they are no longer needed
        merged_df.drop(columns=['site_id', 'name'], inplace=True)

        return merged_df

    def save_raw_data(self, route_df:pd.DataFrame, sites_df:pd.DataFrame, forecast_df:pd.DataFrame) -> pd.DataFrame:
        """
        TODO
        """
        data_to_save = self._data_restructure(route_df, sites_df, forecast_df)

        root = tk.Tk()
        root.withdraw()  # Hide the main window
        root.lift()  # Bring the window to the front
        root.attributes('-topmost', True)  # Keep the window on top of all others
        
        chosen_directory = filedialog.askdirectory(
            initialdir=self.last_save_directory,
            title='Select a Folder to Save Forecast Data'
        )
        
        # If a directory is chosen
        if chosen_directory:
            # Create a new folder named by the current time and forecast product used
            current_time = time.strftime('%Y%m%d_%H%M%S')
            if len(forecast_df.columns) > 10:
                product = 'SF'
            else:
                product = 'CM'
            folder_name = f"{current_time}_{product}"
            new_folder_path = os.path.join(chosen_directory, folder_name)
            os.makedirs(new_folder_path)
            
            # Save each column of data_to_save as a separate CSV
            for column in data_to_save.columns:
                column_data = data_to_save[column].unstack(level=0)
                file_name = f"{column}.csv"
                file_path = os.path.join(new_folder_path, file_name)
                column_data.to_csv(file_path)
            
            # Update the last_save_directory attribute
            self.last_save_directory = new_folder_path

            print(f"Data saved to {new_folder_path}.")
        else:
            print("No directory chosen. Data not saved.")
        
        return data_to_save