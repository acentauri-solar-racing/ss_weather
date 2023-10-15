# https://github.com/Solcast/solcast-api-python-sdk

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
    PERIOD: str = 'PT15M' # Set the period to 15 minutes ISO8601 format

    def __init__(self) -> None:
        self.previous_df = pd.DataFrame()
        self.previous_time: pd.Timestamp = pd.NaT
    
    def _check_variables(self, variables:dict) -> None:
        """ Check if the variables are of the correct type and between the ranges. 
        
            Inputs:
                variables (dict): The variables to be checked. """

        validation_rules = {
            'latitude': (float, constants.GEO['latitude']['min'], constants.GEO['latitude']['max']),
            'longitude': (float, constants.GEO['longitude']['min'], constants.GEO['longitude']['max'])
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
        
    def get_forecast(self, position:dict, checked:bool=False, hours:int=48, print_is_requested:bool=False) -> Tuple[pd.DataFrame, bool]:
        """ """
        if not checked:
            self._check_variables(position)

        try:
            response = forecast.radiation_and_weather(
                latitude=position['latitude'],
                longitude=position['longitude'],
                output_parameters='air_temp,ghi,wind_speed_10m,wind_direction_10m,relative_humidity,precipitation_rate',
                format=self.FORMAT,
                period=self.PERIOD,
                hours=hours,
                api_key=constants.KEY_SOLCAST
            )

        except Exception as e:
            print('No internet connection or another problem')
            return pd.DataFrame(index='time'), False
        
        if print_is_requested:
            print("Solar forecast Solcast have been retrieved.")

        response_df = response.to_pandas()
        response_df.index.name = 'time'
        response_df.index = response_df.index.tz_convert(constants.TIMEZONE)

        # Convert wind speed to km/h
        response_df['wind_speed_10m'] *= 3.6

        # Convert precipitation rate to mm
        response_df['precipitation_rate'] *= int(self.PERIOD.split('T')[1].replace('M', '')) / 60

        return response_df, True
    
    def get_forecasts(self, route_api_df:pd.DataFrame, checked:bool=False, hours_in_advance:int=48, print_is_requested:bool=False) -> pd.DataFrame:
        """ """
        # Check that the dataframe has the right columns
        if 'latitude' not in route_api_df.columns or 'longitude' not in route_api_df.columns or 'cumDistance' not in route_api_df.columns:
            raise ValueError('The dataframe has to have latitude, longitude, and cumDistance columns.')

        # Use apply to get forecasts for each row and store in a list
        forecasts_list = route_api_df.apply(
            lambda row: self.get_forecast(
                {'latitude': row['latitude'], 'longitude': row['longitude']}, checked=checked, hours=hours_in_advance,
                print_is_requested=print_is_requested
            )[0].assign(cumDistance=row['cumDistance']),
            axis=1
        ).tolist()

        if forecasts_list:

            # Concatenate all DataFrames in the list
            result_df = pd.concat(forecasts_list)

            # Set and reorder multi-index
            result_df.set_index('cumDistance', append=True, inplace=True)
            result_df = result_df.reorder_levels(['cumDistance', 'time'])

            # Rename columns
            result_df.rename(columns={
                'air_temp': 'tt',
                'ghi': 'gh',
                'wind_speed_10m': 'ff',
                'wind_direction_10m': 'dd',
                'relative_humidity': 'rh',
                'precipitation_rate': 'rr'
            }, inplace=True)

            local_tz = tzlocal()
            self.previous_time = pd.Timestamp.now(tz=local_tz)
            self.previous_df = result_df

        if print_is_requested:
            print("Solar forecasts Solcast have been retrieved.")

        return result_df

    @property
    def get_solcast_last_time(self) -> pd.Timestamp:
        """ Return the time of the last Solcast solar forecast. """
        return self.previous_time