import pandas as pd
from typing import Tuple
import requests
import json
from bs4 import BeautifulSoup
import CONSTANTS as constants

class ApiParser():
    """
    Class for parsing the API responses.
    """

    def __init__(self) -> None:
        self.column_names = constants.API_COLUMN_NAMES

    def _check_response(self, response:requests.models.Response, function_tag:str) -> None:
        """
        Check if the response is valid.
        """
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
    
    def parse_site_add_response(self, response:requests.models.Response, function_tag:str) -> pd.DataFrame:
        self._check_response(response, function_tag)

        response_dict = response.json()

        # Extract the required information from response_dict
        name_extracted = response_dict["payload"]["solarforecast"]["site"]["name"]
        site_id_extracted = response_dict["payload"]["solarforecast"]["site"]["id"]
        longitude_extracted = response_dict["payload"]["solarforecast"]["site"]["longitude"]
        latitude_extracted = response_dict["payload"]["solarforecast"]["site"]["latitude"]
        altitude_extracted = response_dict["payload"]["solarforecast"]["site"]["altitude"]

        # Create a new DataFrame with extracted values and assign to corresponding columns
        response_data = [[name_extracted, site_id_extracted, longitude_extracted, latitude_extracted, altitude_extracted]]
        response_df = pd.DataFrame(response_data, columns=self.column_names)
        return response_df
    
    def parse_site_info_response(self, response:requests.models.Response, function_tag:str) -> Tuple[pd.DataFrame, str]:
        self._check_response(response, function_tag)

        response_dict = json.loads(response.text)

        # Extract the required information from response_dict
        response_formatted = json.dumps(response_dict, indent=2)

        sites_data = response_dict["payload"]["solarforecast"]["sites"]

        # Create a new DataFrame with extracted values and assign to corresponding columns
        response_df = pd.DataFrame(columns=self.column_names)
        if sites_data != []:
            for site_id, site_info in sites_data.items():
                name_extracted = site_info['name']
                longitude_extracted = site_info['longitude']
                latitude_extracted = site_info['latitude']
                altitude_extracted = site_info['altitude']

                extracted_values = [[name_extracted, int(site_id), longitude_extracted, latitude_extracted, altitude_extracted]]
                response_df = pd.concat([response_df, pd.DataFrame(extracted_values, columns=self.column_names)], ignore_index=True)
        
        return response_df, response_formatted
    
    def parse_solar_forecast_response(self, response: requests.models.Response, function_tag: str) -> pd.DataFrame:
        self._check_response(response, function_tag)

        response_dict = response.json()
        sites_data = response_dict["payload"]["solarforecast"]

        data_to_concat = [
            {
                'site_id': site_id,
                'time': time,
                **time_forecast
            }
            for site_id, site_forecast in sites_data.items()
            for time, time_forecast in site_forecast.items()
        ]

        response_df = pd.DataFrame.from_records(data_to_concat, index=['site_id', 'time'])

        return response_df
    
    def parse_solar_forecast_cloudmove_response(self, response:requests.models.Response, function_tag:str) -> pd.DataFrame:
        self._check_response(response, function_tag)

        # TODO
        response_dict = response.json()

        index = pd.MultiIndex.from_product([[], [], []], names=['space', 'time', 'variable'])

        response_df = pd.DataFrame(response_dict["payload"]["solarforecast"]["sites"])

        return response_df