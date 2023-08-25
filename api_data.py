import time
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import CONSTANTS as costants

class ApiData():
    """
    TODO
    """

    def __init__(self, dataframe:pd.DataFrame) -> None:
        self.column_names = costants.API_COLUMN_NAMES
        self.forecast_sites = pd.DataFrame(columns=self.column_names)
        self.last_save_directory = None

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