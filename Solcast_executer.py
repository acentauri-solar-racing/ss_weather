# https://github.com/Solcast/solcast-api-python-sdk

import requests
import constants
import pandas as pd
from typing import Tuple
from dateutil.tz import tzlocal
from solcast import forecast

class SolcastExecuter():
    """ Class for interacting with the weather forecast API from Solcast.

    Attributes:
        website (str): The base API URL.
        format (str): The response format (default: 'json'). """

    KEY: str = constants.KEY_SOLCAST
    FORMAT: str = 'json'
    PERIOD: str = 'PT15M'

    def __init__(self) -> None:
        self.previous_df = pd.DataFrame()
        self.previous_time: pd.Timestamp = pd.NaT
    
    def _check_variables(self, variables:dict) -> None:
        """ Check if the variables are of the correct type and between the ranges. 
        
            Inputs:
                variables (dict): The variables to be checked. """

        validation_rules = {
            'latitude': (float, -90.0, 90.0),
            'longitude': (float, -180.0, 180.0),
        }

        for variable, value in variables.items():
            if variable in validation_rules:
                value_type, min_value, max_value = validation_rules[variable]

                # Check the type
                if not isinstance(value, value_type):
                    raise ValueError(f'{variable} has to be a {value_type}. Received: {value}')
                
                # Check the range
                if min_value is not None and max_value is not None:
                    if not (min_value <= value <= max_value):
                        raise ValueError(f'{variable} has to be between {min_value} and {max_value}. Received: {value}')
        
    def get_forecast(self, position:dict, print_is_requested:bool=False) -> pd.DataFrame:

        self._check_variables(position)

        response = forecast.radiation_and_weather(
            latitude=position['latitude'],
            longitude=position['longitude'],
            output_parameters='air_temp,ghi,ghi10,ghi90,wind_speed_10m,wind_direction_10m',
            format=self.FORMAT,
            period=self.PERIOD,
            api_key=constants.KEY_SOLCAST
        )

        if print_is_requested:
            print("Solar forecast Solcast have been retrieved.")

        return response.to_pandas()

    def get_forecasts(self, route_api_df: pd.DataFrame, print_is_requested: bool = False) -> pd.DataFrame:
        # Check that the dataframe has the right columns
        if 'latitude' not in route_api_df.columns or 'longitude' not in route_api_df.columns or 'cumDistance' not in route_api_df.columns:
            raise ValueError('The dataframe has to have latitude, longitude, and cumDistance columns.')

        # Create an empty dataframe to store the results
        result_df = pd.DataFrame()

        for _, row in route_api_df.iterrows():
            position = {'latitude': row['latitude'], 'longitude': row['longitude']}
            forecast_df = self.get_forecast(position, print_is_requested=print_is_requested)

            # Rename index
            forecast_df.index.name = 'time'

            # Add cumDistance as a level in the index
            forecast_df.set_index(pd.Series([row['cumDistance']] * len(forecast_df), name='cumDistance'), append=True, inplace=True)

            # Concatenate to the result dataframe
            result_df = pd.concat([result_df, forecast_df])

        # Reorder index levels
        result_df = result_df.reorder_levels(['cumDistance', 'time'])

        # Rename columns
        result_df.rename(columns={
            'air_temp': 'tt',
            'ghi': 'gh',
            'wind_speed_10m': 'ff',
            'wind_direction_10m': 'dd'
        }, inplace=True)

        return result_df

    @property
    def get_solcast_last_time(self) -> pd.Timestamp:
        """ Return the time of the last Solcast solar forecast. """
        return self.previous_time