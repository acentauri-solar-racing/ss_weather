import os
import time
import psychrolib # Psychrometric conversion library https://github.com/psychrometrics/psychrolib (Installation: https://pypi.org/project/PsychroLib/, Documentation: https://psychrometrics.github.io/psychrolib/api_docs.html)
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog
from typing import Tuple
from dateutil.tz import tzlocal

class Preprocessor():
    """ Class for preprocessing the forecast data and making them ready for Dynamic Programming and Model Predictive Control.
    
    Attributes:
        print_is_requested (bool): Whether to print the preprocessing steps.
        route_df (pd.DataFrame): The route dataframe with cumDistance and time columns.
        sites_df (pd.DataFrame): The sites dataframe with name and site_id columns.
        forecast_df (pd.DataFrame): The forecast dataframe with site_id and time columns.
        preprocess_df (pd.DataFrame): The forecast dataframe with cumDistance and time columns. """
    
    # Constants for wind log correction
    ROUGHNESS_LENGTH_Z0 = 0.03 # in meters from roughness class 1 (https://wind-data.ch/tools/profile.php?h=10&v=5&z0=0.03&abfrage=Refresh)
    REFERENCE_HEIGHT_H1 = 10.0 # in meters
    WIND_HEIGHT_H2 = 0.5 # in meters
    CORRECTING_FACTOR = np.log(WIND_HEIGHT_H2 / ROUGHNESS_LENGTH_Z0) / np.log(REFERENCE_HEIGHT_H1 / ROUGHNESS_LENGTH_Z0)

    def __init__(self, print_is_requested:bool=False) -> None:
        self.print_is_requested = print_is_requested
        self.last_save_directory:str = ''

        self.route_df = pd.DataFrame()
        self.sites_df = pd.DataFrame()
        self.forecast_df = pd.DataFrame()
        self.preprocess_df = pd.DataFrame()

    def _print(self, message:str) -> None:
        """ Print the message if print_is_requested is True. """
        if self.print_is_requested:
            print(message)

    def _data_restructure(self, raw_forecast_df:pd.DataFrame) -> pd.DataFrame:
        """ Restructure the forecast data to have cumDistance as the index and time as the columns.
        
            Inputs:
                raw_forecast_df (pd.DataFrame): The forecast dataframe with site_id and time columns."""
        
        # Convert the index of route_df to object (string) type
        self.route_df.index = self.route_df.index.astype(str)
        
        # Given a site_id from processing_df, find the corresponding name from sites_df, find the cumDistance from route_df
        index_forecast = raw_forecast_df.index.get_level_values('site_id').unique()
        index_sites = self.sites_df.index

        # Check that the indices are the same
        if not index_forecast.equals(index_sites):
            raise ValueError('The index of the forecast dataframe and the sites dataframe are not the same')

        # Merge forecast_df with sites_df on site_id to get the name
        restructured_df = raw_forecast_df.reset_index().merge(self.sites_df[['name']], left_on='site_id', right_index=True)

        # Merge the result with route_df on name to get cumDistance
        restructured_df = restructured_df.merge(self.route_df[['cumDistance']], left_on='name', right_index=True)

        # Set the index to cumDistance and time
        restructured_df.set_index(['cumDistance', 'time'], inplace=True)

        # Drop the site_id and name columns as they are no longer needed
        restructured_df.drop(columns=['site_id', 'name'], inplace=True)

        return restructured_df

    def _data_cut_time(self, hours_in_advance:int) -> None:
        """ Cut the forecast data to the specified hours in advance.
        
            Inputs:
                hours_in_advance (int): The number of hours in advance to keep. """
        
        if hours_in_advance is None:
            return
        
        # Get the timezone of the machine (it depends on the settings) and create a time-aware Timestamp
        local_tz = tzlocal()
        now = pd.Timestamp.now(tz=local_tz)

        # Drop past columns: less than now less 15 min to keep last row
        self.preprocess_df = self.preprocess_df[self.preprocess_df.index.get_level_values('time').tz_convert('UTC') >= now.tz_convert('UTC') - pd.Timedelta(minutes=15)]
        
        # Drop future columns: more than x hours and 15 minutes
        self.preprocess_df = self.preprocess_df[self.preprocess_df.index.get_level_values('time').tz_convert('UTC') <= now.tz_convert('UTC') + pd.Timedelta(hours=hours_in_advance, minutes=15)]

        self._print(f'Forecast data cut to {hours_in_advance} hours in advance.')

    def _temperature_correction(self) -> None:
        """ Correct the temperature forecast with the corrections suggested by Pascal Graf from Meteotest in °C. """

        # Extract the time values from the multi-index
        times_hours = self.preprocess_df.index.get_level_values('time').hour

        # Apply corrections based on the time
        mask_night = (times_hours >= 20) | (times_hours <= 8)
        mask_day = (times_hours >= 10) & (times_hours <= 16)

        self.preprocess_df.rename(columns={'tt': 'temperature'}, inplace=True)

        # Apply the corrections
        self.preprocess_df.loc[mask_night, 'temperature'] -= 2 # Subtract 2°C during the night
        self.preprocess_df.loc[mask_day, 'temperature'] += 3 # Add 3°C during the day
        # No correction is applied for the in-between times as they remain unchanged

        self._print(f'Temperature correction applied.')

    def _wind_log_correction(self) -> None:
        """ Correct the wind speed and gust forecast at 10 meters to the wind speed at 0.5 meters in m/s.
            Equation taken from:
            https://wind-data.ch/tools/profile.php?h=10&v=5&z0=0.03&abfrage=Refresh. """

        self.preprocess_df.rename(columns={'ff': 'windSpeed', 'fx': 'windGust'}, inplace=True)

        self.preprocess_df[['windSpeed', 'windGust']] *= self.CORRECTING_FACTOR / 3.6 # Convert from km/h to m/s

        self._print(f'Wind log correction applied.')

    def _wind_decomposition(self) -> None:
        """ Decompose the wind forecast at 0.5 meters to side and front wind in m/s. """

        self.preprocess_df.rename(columns={'dd': 'windDirection'}, inplace=True)
        
        # Extract relevant angles (mapping needed to adjust sizes)
        theta = self.route_df.set_index('cumDistance')['theta'] # set cumDistance as the index for theta
        theta_mapped = self.preprocess_df.index.get_level_values('cumDistance').map(theta) # Map the cumDistance level of wind_direction's index to the values in theta
        attack_angle = self.preprocess_df['windDirection'] - theta_mapped # in degrees

        # Calculate wind speed components in m/s
        self.preprocess_df['sideWind'] = self.preprocess_df['windSpeed'] * np.sin(np.radians(attack_angle)) / 3.6
        self.preprocess_df['frontWind'] = self.preprocess_df['windSpeed'] * np.cos(np.radians(attack_angle)) / 3.6

        self._print(f'Wind decomposition applied.')

    def _air_density_estimation(self) -> None:
        """ Estimate the air density from the altitude, temperature and relative humidity.
            Equation taken from:
            https://wind-data.ch/tools/luftdichte.php?method=2&pr=990&t=25&rh=99&abfrage2=Aktualisieren. """
        
        psychrolib.SetUnitSystem(psychrolib.SI)

        # Extract altitude data and calculate atmospheric pressure
        altitude = self.route_df.set_index('cumDistance')['altitudeSmoothed'] # set cumDistance as the index for altitude (in meters)
        pressure = altitude.apply(psychrolib.GetStandardAtmPressure) # in Pa
        self.preprocess_df['pressure'] = self.preprocess_df.index.get_level_values('cumDistance').map(pressure) # Map the cumDistance level of pressure's index to the values in pressure

        # Calculate humidity ratio
        self.preprocess_df['humidity_ratio'] = self.preprocess_df.apply( # in kg_H₂O kg_Air⁻¹ [SI]
            lambda row: psychrolib.GetHumRatioFromRelHum(
                TDryBulb=row['temperature'], # in °C
                RelHum=row['rh']/100, # in %
                Pressure=row['pressure'] # in Pa
            ), 
            axis=1
        )
        # Calculate air density
        self.preprocess_df['airDensity'] = self.preprocess_df.apply( # in kg_Air m⁻³ [SI]
            lambda row: psychrolib.GetMoistAirDensity(
                TDryBulb=row['temperature'], # in °C
                HumRatio=row['humidity_ratio'], # in kg_H₂O kg_Air⁻¹ [SI]
                Pressure=row['pressure'] # in Pa
            ), 
            axis=1
        )
        # Drop unnecessary columns
        self.preprocess_df.drop(columns=['rh', 'pressure', 'humidity_ratio'], inplace=True)

        self._print(f'Air density estimation applied.')

    def preprocess(self, route_df:pd.DataFrame, sites_df:pd.DataFrame, raw_forecast_df:pd.DataFrame, hours_in_advance:int=None, print_is_requested:bool=False) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """ Preprocess the forecast data and make them ready for Dynamic Programming and Model Predictive Control.
        
            Inputs:
                route_df (pd.DataFrame): The route dataframe with cumDistance and time columns.
                sites_df (pd.DataFrame): The sites dataframe with name and site_id columns.
                forecast_df (pd.DataFrame): The forecast dataframe with site_id and time columns.
                hours_in_advance (int): The number of hours in advance to keep.
                print_is_requested (bool): Whether to print the preprocessing steps. """
        
        self.print_is_requested = print_is_requested
        self.route_df = route_df
        self.sites_df = sites_df

        self.forecast_df = self._data_restructure(raw_forecast_df)

        # Restructure and correct the data for Dynamic Programming and Model Predictive Control
        # Distinguish between the two forecast products
        if len(self.forecast_df.columns) < 10:
            # CloudMove
            column_name = ['tt', 'gh']
            self.preprocess_df = self.forecast_df[column_name].copy()

            self._data_cut_time(hours_in_advance)
            self._temperature_correction()

        else:
            # SolarForecast
            column_name = ['tt', 'gh', 'rh', 'ff', 'dd', 'fx']
            self.preprocess_df = self.forecast_df[column_name].copy()

            self._data_cut_time(hours_in_advance)
            self._temperature_correction()
            self._wind_log_correction()
            self._wind_decomposition()
            self._air_density_estimation()

        # Rename global irradiance column
        self.preprocess_df.rename(columns={'gh': 'globalIrradiance'}, inplace=True) # in W m⁻²

        # Round to 3 decimals
        self.forecast_df = self.forecast_df.round(3)
        self.preprocess_df = self.preprocess_df.round(3)

        return self.forecast_df, self.preprocess_df
    
    def save_data2folder(self) -> None:
        """ Save the raw forecast data and the preprocessed data to CSV files. """

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

            # Distinguish between the two forecast products
            if len(self.forecast_df.columns) > 10:
                product = 'SF'
            else:
                product = 'CM'

            # Create the new folder
            folder_name = f"{current_time}_{product}"
            new_folder_path = os.path.join(chosen_directory, folder_name)
            os.makedirs(new_folder_path)
            self.last_save_directory = new_folder_path # Update the last_save_directory attribute


            # Save the chosen columns for MPC and DP
            self.route_df[['cumDistance', 'maxSpeed', 'inclinationSmoothed']].to_csv(os.path.join(new_folder_path, 'route.csv'))


            # Create a subfolder for the raw forecast data
            forecast_folder_path = os.path.join(new_folder_path, 'raw')
            os.makedirs(forecast_folder_path)

            # Save each column of data_to_save as a separate CSV
            for column in self.forecast_df.columns:
                column_data = self.forecast_df[column].unstack(level=0)
                file_name = f"{column}.csv"
                file_path = os.path.join(forecast_folder_path, file_name)
                column_data.to_csv(file_path)


            # Create a subfolder for the preprocessed data
            preprocess_folder_path = os.path.join(new_folder_path, 'preprocess')
            os.makedirs(preprocess_folder_path)
            
            # Save each column of data_to_save as a separate CSV
            for column in self.preprocess_df.columns:
                column_data = self.preprocess_df[column].unstack(level=0)
                file_name = f"{column}.csv"
                file_path = os.path.join(preprocess_folder_path, file_name)
                column_data.to_csv(file_path)

            print(f"Data saved to {new_folder_path}.")
        else:
            print("No directory chosen. Data not saved.")