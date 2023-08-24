import time
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from api_requester import ApiRequester

class Amplifier():
    """
    TODO
    """

    def __init__(self) -> None:
        pass

    def add_sites(self, dataframe:pd.DataFrame, print_is_requested:bool=True) -> None:
        """
        TODO
        """
        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError('dataframe must be a Pandas DataFrame.')

        for index, row in dataframe.iterrows():
            name = str(index)
            latitude = row['latitude']
            longitude = row['longitude']
            cumDistance = row['cumDistance']
            # TODO CHECK DATAFRAME STRUCTURE

            ApiRequester.get_site_add(name=name, latitude=latitude, longitude=longitude, print_is_requested=print_is_requested)

        if print_is_requested:
            print("Requested sites have been added.")
            print(ApiRequester.forecast_sites)

    def delete_sites(self, dataframe:pd.DataFrame, print_is_requested:bool=True) -> None:
        """
        TODO
        """
        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError('dataframe must be a Pandas DataFrame.')

        for _, row in dataframe.iterrows():
            site_id = row['site_id']
            # TODO CHECK DATAFRAME STRUCTURE

            ApiRequester.get_site_delete(site_id, print_is_requested=print_is_requested)

        if print_is_requested:
            print("Requested sites have been deleted.")
            print(ApiRequester.forecast_sites)

    def delete_all_sites(self, print_is_requested:bool=True) -> None:
        """
        TODO
        """
        for _, row in ApiRequester.forecast_sites.iterrows():
            site_id = row['site_id']
            ApiRequester.get_site_delete(site_id, print_is_requested=print_is_requested)
        
        if print_is_requested:
            print("All sites have been deleted.")
            print(ApiRequester.forecast_sites)

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
            ApiRequester.forecast_sites.to_csv(f'forecast_sites_{current_time}.csv', file_path, index=False)
            print(f'Forecast sites saved to {file_path}')
            
            # Remember the chosen directory for next time
            ApiRequester.last_save_directory = '/'.join(file_path.split('/')[:-1])