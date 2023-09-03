import time
import pandas as pd
import tkinter as tk
from tkinter import filedialog

class ApiSaver():
    """
    TODO
    """

    def __init__(self) -> None:
        self.last_save_directory = None

    def _data_restructure(self, route_df:pd.DataFrame, ) -> pd.DataFrame:
        """
        TODO
        """
        pass

    def save_raw_data(self) -> None:
        """
        TODO
        """
        # CALL FUNCTION THAT SEPARATES THE DATAFRAME IN DIFFERENT DATAFRAMES FOR EACH VARIABLE
        # SHOULD BE ABLE TO HANDLE CLOUDMOVE AND SOLARFORECAST OUTPUTS

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