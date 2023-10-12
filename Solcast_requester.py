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
        
    # WEBSITE: str = 'https://api.solcast.com.au/data'
    KEY: str = constants.KEY_SOLCAST
    FORMAT: str = 'json'
    # TIMEOUT: int = 10


    # TYPE: str = '/forecast'
    # ACTION: str = '/radiation_and_weather'


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
        
    def get_forecast(self, position:dict) -> pd.DataFrame:

        self._check_variables(position)

        response = forecast.radiation_and_weather(
            latitude=position['latitude'],
            longitude=position['longitude'],
            output_parameters='air_temp,ghi,ghi10,ghi90,wind_speed_10m,wind_direction_10m',
            format=self.FORMAT,
            api_key=constants.KEY_SOLCAST
        )

        return response.to_pandas()

    def get_forecasts(self, route:pd.DataFrame) -> pd.Dataframe:
        pass