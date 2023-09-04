import os
import time
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog
import psychrolib # Psychrometric conversion library https://github.com/psychrometrics/psychrolib (Installation: https://pypi.org/project/PsychroLib/, Documentation: https://psychrometrics.github.io/psychrolib/api_docs.html)

class ForecastPreprocessor():
    """
    TODO
    """

    def __init__(self, print_is_requested:bool=False) -> None:
        self.ROUGHNESS_LENGTH_Z0 = 0.03 # in meters from roughness class 1 (https://wind-data.ch/tools/profile.php?h=10&v=5&z0=0.03&abfrage=Refresh)
        self.REFERENCE_HEIGHT_H1 = 10.0 # in meters
        self.WIND_HEIGHT_H2 = 0.5 # in meters
        self.CORRECTING_FACTOR = np.log(self.WIND_HEIGHT_H2 / self.ROUGHNESS_LENGTH_Z0) / np.log(self.REFERENCE_HEIGHT_H1 / self.ROUGHNESS_LENGTH_Z0)
        self.print_is_requested = print_is_requested

        self.route_df : pd.DataFrame = pd.DataFrame()
        self.processing_df : pd.DataFrame = pd.DataFrame()

    def _print(self, message:str) -> None:
        if self.print_is_requested:
            print(message)

    def _data_cut_time(self, hours_in_advance:int) -> None:
        """
        TODO
        """
        # Drop past columns: less than now less 15 min to keep last row
        now = pd.Timestamp.now()
        self.processing_df = self.processing_df[self.processing_df.index.get_level_values('time') >= now - pd.Timedelta(minutes=15)]
        
        # Drop future columns: more than x hours
        self.processing_df = self.processing_df[self.processing_df.index.get_level_values('time') <= now + pd.Timedelta(hours=hours_in_advance, minutes=15)]

        self._print(f'Forecast data cut to {hours_in_advance} hours in advance. \n {self.processing_df}')

    def _temperature_correction(self) -> None:
        """
        Corrections suggested by Pascal Graf from Meteotest.
        """
        # Extract the time values from the multi-index
        times_hours = self.processing_df.index.get_level_values('time').hour

        # Apply corrections based on the time
        mask_night = (times_hours >= 20) | (times_hours <= 8)
        mask_day = (times_hours >= 10) & (times_hours <= 16)

        # Change column name
        self.processing_df.rename(columns={'tt': 'temperature'}, inplace=True)

        # Apply the corrections
        self.processing_df.loc[mask_night, 'temperature'] -= 2 # Subtract 2°C during the night
        self.processing_df.loc[mask_day, 'temperature'] += 3 # Add 3°C during the day
        # No correction is applied for the in-between times as they remain unchanged

        self._print(f'Temperature correction applied. \n {self.processing_df}')

    def _wind_log_correction(self) -> None:
        """
        Correct the wind speed forecast at 10 meters to the wind speed at 0.5 meters.
        Equation taken from: https://wind-data.ch/tools/profile.php?h=10&v=5&z0=0.03&abfrage=Refresh
        """
        self.processing_df.rename(columns={'ff': 'windSpeed'}, inplace=True)
        self.processing_df *= self.CORRECTING_FACTOR / 3.6 # Convert from km/h to m/s

        self._print(f'Wind log correction applied. \n {self.processing_df}')

    def _wind_decomposition(self) -> None:
        """
        TODO
        """
        # Extract relevant angles
        wind_direction = self.processing_df['dd'] # in degrees
        theta = self.route_df.set_index('cumDistance')['theta'] # set cumDistance as the index for theta
        theta_mapped = wind_direction.index.get_level_values('cumDistance').map(theta) # Map the cumDistance level of wind_direction's index to the values in theta
        attack_angle = wind_direction - theta_mapped # in degrees
        
        # theta_mapped = self.processing_df.index.get_level_values('cumDistance').map(self.route_df.set_index('cumDistance')['theta'])
        # attack_angle = self.processing_df['dd'] - theta_mapped

        # Calculate wind speed components
        self.processing_df['sideWind'] = self.processing_df['windSpeed'] * np.sin(np.radians(attack_angle)) / 3.6
        self.processing_df['frontWind'] = self.processing_df['windSpeed'] * np.cos(np.radians(attack_angle)) / 3.6

        self._print(f'Wind decomposition applied. \n {self.processing_df}')

    def _air_density_estimation(self) -> None:
        """
        TODO https://wind-data.ch/tools/luftdichte.php?method=2&pr=990&t=25&rh=99&abfrage2=Aktualisieren
        """
        psychrolib.SetUnitSystem(psychrolib.SI)
        altitude_mapped = self.processing_df.index.get_level_values('cumDistance').map(self.route_df.set_index('cumDistance')['altitudeSmoothed'])
        atmospheric_pressure = psychrolib.GetStandardAtmPressure(Altitude=altitude_mapped)
        humidity_ratio = psychrolib.GetHumRatioFromRelHum(TDryBulb=self.processing_df['temperature'], RelHum=self.processing_df['rh']/100, Pressure=atmospheric_pressure)
        self.processing_df['airDensity'] = psychrolib.GetMoistAirDensity(TDryBulb=self.processing_df['temperature'], HumRatio=humidity_ratio, Pressure=atmospheric_pressure)
        self._print(f'Air density estimation applied. \n {self.processing_df}')


        # # Extract altitude data and calculate atmospheric pressure
        # altitude = self.route_df['altitudeSmoothed'] # in meters
        # altitude_mapped = self.processing_df.index.get_level_values('cumDistance').map(altitude)
        # atmospheric_pressure = psychrolib.GetStandardAtmPressure(Altitude=altitude_mapped) # in Pa

        # # Extract temperature and relative humidity data and calculate humidity ratio
        # air_temperature = self.processing_df['temperature'] # in °C
        # relative_humidity = self.processing_df['rh'] # in %
        # humidity_ratio = psychrolib.GetHumRatioFromRelHum(TDryBulb=air_temperature, RelHum=relative_humidity/100, Pressure=atmospheric_pressure) # in kg_H₂O kg_Air⁻¹ [SI]

        # # Calculate air density
        # density = psychrolib.GetMoistAirDensity(TDryBulb=air_temperature, HumRatio=humidity_ratio, Pressure=atmospheric_pressure) # in kg m⁻³ [SI]

        # density_df = pd.DataFrame(density, columns=['airDensity'])
        # self.processing_df = pd.concat([self.processing_df, density_df], axis=1)

        # self._print(f'Air density estimation applied. \n {self.processing_df}')

    def forecast_preprocessing(self, route_df:pd.DataFrame, forecast_df:pd.DataFrame, hours_in_advance:int, print_is_requested:bool=False) -> pd.DataFrame:
        """
        TODO
        """
        if not isinstance(route_df, pd.DataFrame) or not isinstance(forecast_df, pd.DataFrame):
            raise ValueError("Input data should be of type pandas DataFrame")
        
        self.print_is_requested = print_is_requested
        self.route_df = route_df

        # Distinguish between the two forecast products
        if len(forecast_df.columns) < 10:
            # CloudMove
            column_name = ['tt', 'gh']
            self.processing_df = forecast_df[column_name].copy()

            self._data_cut_time(hours_in_advance)
            self._temperature_correction()

        else:
            # SolarForecast
            column_name = ['tt', 'gh', 'rh', 'ff', 'dd', 'fx']
            self.processing_df = forecast_df[column_name].copy()

            self._data_cut_time(hours_in_advance)
            self._temperature_correction()
            self._wind_log_correction()
            self._wind_decomposition()
            # self._air_density_estimation()

        return self.processing_df
    
    def save_data(self, route_df:pd.DataFrame, sites_df:pd.DataFrame, forecast_df:pd.DataFrame) -> pd.DataFrame:
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