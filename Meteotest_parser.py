import requests
import json
import pytz
import pandas as pd
from typing import Tuple
from bs4 import BeautifulSoup

class MeteotestParser():
    """ Class for parsing the API responses. """

    def __init__(self) -> None:
        pass

    def _check_response(self, response:requests.models.Response, function_tag:str) -> None:
        """ Check if the response is valid. Default response type is JSON.
        
            Inputs:
                response (requests.models.Response): The response object.
                function_tag (str): The name of the function that called this method. """

        content_type = response.headers.get('Content-Type')

        if 'application/json' in content_type:
            response_dict = response.json() # equivalent to = json.loads(response.text)
            print(f'Response status from {function_tag}: {response_dict["status"]}.')

        elif 'text/html' in content_type:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find the <div> with class "alert alert-info" and get its text
            info_div = soup.find('div', class_='alert alert-info')
            if info_div:
                status_text = info_div.get_text().strip()
                print(f'Response status from {function_tag}: {status_text}.')

        else:
            print(f'Unknown content type from {function_tag}.')

    def _convert_to_timedelta(self, utc_string:str) -> pd.Timedelta:
        """ Convert a UTC offset string to a Timedelta object. 
        
            Inputs:
                utc_string (str): The UTC offset string. """

        offset_str = utc_string.replace("UTC", "")
        utc_delta = pd.Timedelta(hours=float(offset_str))

        return utc_delta
    
    def parse_site_add_response(self, response:requests.models.Response, function_tag:str) -> pd.DataFrame:
        """ Parse the response from the site_add function.
        
            Inputs:
                response (requests.models.Response): The response object.
                function_tag (str): The name of the function that called this method. """
        
        self._check_response(response, function_tag)

        response_dict = response.json()
        sites_data = response_dict["payload"]["solarforecast"]["site"]

        # Check if the response is empty
        if not sites_data:
            print(f'Response from {function_tag} is empty.')
            return pd.DataFrame()

        # Extract the required information from site_data
        data_to_concat = [{
            'site_id': int(sites_data["id"]),
            'name': sites_data["name"],
            'longitude': sites_data["longitude"],
            'latitude': sites_data["latitude"],
            'altitude': sites_data["altitude"],
            'UTC_offset': self._convert_to_timedelta(sites_data["utc_offset"])
        }]
        response_df = pd.DataFrame.from_records(data_to_concat, index=['site_id'])

        return response_df
    
    def parse_site_info_response(self, response:requests.models.Response, function_tag:str) -> Tuple[pd.DataFrame, str]:
        """ Parse the response from the site_info function.
        
            Inputs:
                response (requests.models.Response): The response object.
                function_tag (str): The name of the function that called this method. """
        
        self._check_response(response, function_tag)

        response_dict = response.json()
        sites_data = response_dict["payload"]["solarforecast"]["sites"]

        # Format the response for output
        response_formatted = json.dumps(response_dict, indent=2)

        # Check if the response is empty
        if not sites_data:
            print(f'Response from {function_tag} is empty.')
            return pd.DataFrame(), response_formatted

        data_to_concat = [
            {
                'site_id': int(site_id),
                'name': site_info['name'],
                'longitude': site_info['longitude'],
                'latitude': site_info['latitude'],
                'altitude': site_info['altitude'],
                'UTC_offset': self._convert_to_timedelta(site_info['utc_offset'])
            }
            for site_id, site_info in sites_data.items()
        ]
        response_df = pd.DataFrame.from_records(data_to_concat, index=['site_id'])

        return response_df, response_formatted
    
    def parse_solar_forecast_response(self, response:requests.models.Response, forecast_sites:pd.DataFrame, function_tag:str) -> pd.DataFrame:
        """ Parse the response from the solar_forecast and _cloudmove functions.
            The output time depends on the timezone of the first point!
        
            Inputs:
                response (requests.models.Response): The response object.
                forecast_sites (pd.DataFrame): The dataframe with the forecast sites information.
                function_tag (str): The name of the function that called this method. """
        
        self._check_response(response, function_tag)

        response_dict = response.json()
        sites_data = response_dict["payload"]["solarforecast"]

        # Check if the response is empty
        if not sites_data:
            print(f'Response from {function_tag} is empty.')
            return pd.DataFrame()
        
        # NB: The times are changed with respect to the first point!
        data_to_concat = [
            {
                'site_id': int(site_id),
                'time': (pd.to_datetime(time, format='%Y-%m-%d %H:%M:%S')
                        .tz_localize('UTC')
                        .astimezone(pytz.FixedOffset(forecast_sites.loc[int(site_id), 'UTC_offset'].total_seconds() / 60))),
                **time_forecast
            }
            for site_id, site_forecast in sites_data.items()
            for time, time_forecast in site_forecast.items()
        ]

        response_df = pd.DataFrame.from_records(data_to_concat, index=['site_id', 'time'])

        # Force the index to be a DatetimeIndex
        if not isinstance(response_df.index.get_level_values('time'), pd.DatetimeIndex):
            response_df.index.set_levels([pd.to_datetime(response_df.index.get_level_values('time'))], level='time', inplace=True)

        return response_df