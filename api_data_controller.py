import time
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import CONSTANTS as costants
from api_requester import ApiRequester

class ApiDataController():
    """
    TODO
    """

    def __init__(self) -> None:
        self.column_names = costants.API_COLUMN_NAMES
        self.forecast_sites = pd.DataFrame(columns=self.column_names)

        # Retrieve site information and populate the forecast_sites DataFrame
        response_pd, _ = ApiRequester.get_site_info(print_is_requested=False)

        self.forecast_sites = pd.concat([self.forecast_sites, response_pd], ignore_index=True)

        print(f"Current sites' info has been retrieved. \n {self.forecast_sites}")

    def modify_site_add_data(self, dataframe:pd.DataFrame, print_is_requested:bool=True) -> None:
        """
        TODO
        """
        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError('dataframe must be a Pandas DataFrame.')
        
        # Update the forecast_sites DataFrame
        self.forecast_sites = pd.concat([self.forecast_sites, dataframe], ignore_index=True)

        if print_is_requested:
            print(f"Add site has been saved: \n {self.forecast_sites}")

    def modify_site_edit_data(self, site_id:int, print_is_requested:bool=True, **kwargs) -> None:
        """
        TODO
        """
        # Update the forecast_sites DataFrame
        if 'name' in kwargs:
            self.forecast_sites.loc[self.forecast_sites['site_id'] == site_id, 'name'] = kwargs['name']
        
        if 'position' in kwargs:
            position = kwargs['position']
            self.forecast_sites.loc[self.forecast_sites['site_id'] == site_id, 'longitude'] = position['longitude']
            self.forecast_sites.loc[self.forecast_sites['site_id'] == site_id, 'latitude'] = position['latitude']

        if print_is_requested:
            print(f"Edit site has been saved: \n {self.forecast_sites}.")

    def modify_site_delete_data(self, site_id:int, print_is_requested:bool=True) -> None:
        """
        TODO
        """
        # Update the forecast_sites DataFrame
        self.forecast_sites = self.forecast_sites[self.forecast_sites['site_id'] != site_id]

        if print_is_requested:
            print(f"Delete site has been saved: \n {self.forecast_sites}.")

    def save_raw_data(self) -> None:
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Remember the last chosen directory
        initial_dir = getattr(self, 'last_save_directory', '')
        
        file_path = filedialog.asksaveasfilename(
            initialdir=initial_dir,
            title='Save Forecast Sites as CSV',
            filetypes=[('CSV files', '*.csv')]
        )
        
        if file_path:
            current_time = time.strftime("%Y%m%d-%H%M%S")
            self.forecast_sites.to_csv(f'forecast_sites_{current_time}.csv', file_path, index=False)
            print(f'Forecast sites saved to {file_path}')
            
            # Remember the chosen directory for next time
            self.last_save_directory = '/'.join(file_path.split('/')[:-1])