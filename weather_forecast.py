import requests
import time
import json
import pandas as pd
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import filedialog

class WeatherForecast():
    """
    Class for interacting with the weather forecast API from Meteotest.

    Attributes:
        api_website (str): The base API URL.
        key (str): The API key for authentication.
        service (str): The service to be used.
        format (str): The response format (default: 'json').
    """
        
    api_website: str = 'https://mdx.meteotest.ch/api_v1?'
    key: str = '54F773F38E50F4CF562384A44B9948D3'
    service: str = 'solarforecast'
    format: str = 'json'

    def __init__(self) -> None:
        self.column_names = ['name', 'site_id', 'longitude', 'latitude']
        self.forecast_sites = pd.DataFrame(columns=self.column_names)

        # Retrieve site information and populate the forecast_sites DataFrame
        response = self.get_site_info(print_is_requested=False)
        response_dict = response.json()
        sites_data = response_dict["payload"]["solarforecast"]["sites"]

        if sites_data != []:
            for site_id, site_info in sites_data.items():
                name_extracted = site_info['name']
                longitude_extracted = site_info['longitude']
                latitude_extracted = site_info['latitude']

                extracted_values = [[name_extracted, int(site_id), longitude_extracted, latitude_extracted]]
                extracted_values_pd = pd.DataFrame(extracted_values, columns=self.column_names)

                self.forecast_sites = pd.concat([self.forecast_sites, extracted_values_pd], ignore_index=True)
        # TODO IMPROVE PRINT
        print("Current sites:")
        print(self.forecast_sites)
    
    def _check_variables(self, variables:dict) -> None:
        """
        Check if the variables are valid.
        """
        validation_rules = { # horizon, hddctin, hddctout, and cddctout are not included
            'site_id': (int, None, None),
            'name': (str, None, None),
            'action': (str, None, None),
            'format': (str, None, None),
            'latitude': (float, -90.0, 90.0),
            'longitude': (float, -180.0, 180.0),
            'azimuth': (int, 0, 360),
            'inclination': (int, 0, 90),
            'altitude': (int, None, None)
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
                    
                # Check site id
                # if variable == 'site_id':
                    # response = self.get_site_info(print_is_requested=False)
                    # response_dict = response.json()
                    
                    # sites_id = response_dict["payload"]["solarforecast"]["sites"].keys()
                    # if str(value) not in set(sites_id):
                    #     raise ValueError(f'Site ID {value} is not valid.')
            
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
            
    def _send_get_request(self, variables:dict) -> requests.models.Response:
        """
        Format the URL and send a GET request.
        """
        self._check_variables(variables)

        mdx_url = f'{self.api_website}key={self.key}&service={self.service}'
        for key, value in variables.items():
            mdx_url += f'&{key}={value}'

        response = requests.get(mdx_url, timeout=10)

        self._check_response(response, function_tag=variables["action"])
        return response

    def get_site_add(self, name:str, latitude:float, longitude:float, azimuth:int=0, inclination:int=0, print_is_requested:bool=True) -> None:
        """
        TODO
        """
        variables = { # altitude, horizon, hddctin, hddctout, and cddctout are not included
            'action': 'siteadd',
            'format': self.format,
            'name': name,
            'latitude': latitude,
            'longitude': longitude,
            'azimuth': azimuth,
            'inclination': inclination
        }
        response = self._send_get_request(variables)
        response_dict = response.json()

        # Extract the required information from response_dict
        site_id_extracted = response_dict["payload"]["solarforecast"]["site"]["id"]
        longitude_extracted = response_dict["payload"]["solarforecast"]["site"]["longitude"]
        latitude_extracted = response_dict["payload"]["solarforecast"]["site"]["latitude"]

        # Create a new DataFrame with extracted values and assign to corresponding columns
        response_data = [[name, site_id_extracted, longitude_extracted, latitude_extracted]]
        response_df = pd.DataFrame(response_data, columns=self.column_names)

        self.forecast_sites = pd.concat([self.forecast_sites, response_df], ignore_index=True)

        if print_is_requested:
            print(f'Site with name {name} has been added.')

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

            self.get_site_add(name=name, latitude=latitude, longitude=longitude, print_is_requested=print_is_requested)

        if print_is_requested:
            print("All sites have been added.")
            print(self.forecast_sites)

    def get_site_edit(self, site_id:int, print_is_requested:bool=True, **kwargs) -> None:
        """
        Edit name or position (longitude and latitude)
        """
        variables = {
            'action': 'siteedit',
            'site_id': site_id
        }
        string = ""

        # Check if kwargs contains 'name' or 'position'
        if 'name' in kwargs:
            variables['name'] = kwargs['name']
            string += f"New name: {kwargs['name']}. "

        if 'position' in kwargs:
            position = kwargs['position']
            if isinstance(position, dict) and 'longitude' in position and 'latitude' in position:
                variables['longitude'] = position['longitude']
                variables['latitude'] = position['latitude']
                string += f"New position: {kwargs['position']}. "
            else:
                raise ValueError("Position should be a dictionary with 'longitude' and 'latitude' keys.")

        self._send_get_request(variables)

        if print_is_requested:
            print(f"Site with ID {site_id} has been edited: {string}")

    def get_site_delete(self, site_id:int, print_is_requested:bool=True) -> None:
        """
        TODO
        """
        variables = {
            'action': 'sitedelete',
            'site_id': site_id
        }
        self._send_get_request(variables)

        self.forecast_sites = self.forecast_sites[self.forecast_sites['site_id'] != site_id]

        if print_is_requested:
            print(f'Site with id {site_id} has been removed.')

    def delete_all_sites(self, print_is_requested:bool=True) -> None:
        """
        TODO
        """
        for _, row in self.forecast_sites.iterrows():
            site_id = row['site_id']
            self.get_site_delete(site_id, print_is_requested=print_is_requested)
        
        if print_is_requested:
            print("All sites have been deleted.")
            print(self.forecast_sites)

    def get_site_info(self, print_is_requested:bool=True) -> requests.models.Response:
        """
        TODO
        """
        variables = {
            'action': 'siteinfo',
            'format': self.format
        }
        response = self._send_get_request(variables)

        if print_is_requested:
            response_formatted = json.loads(response.text)
            print(json.dumps(response_formatted, indent=2))
        return response

    def get_solar_forecast(self) -> pd.DataFrame:
        """
        TODO
        """
        variables = {
            'action': 'getforecast',
            'format': self.format
        }
        response = self._send_get_request(variables)

        response_dict = response.json()
        response_pd = pd.DataFrame(response_dict["payload"]["solarforecast"]["sites"])
        return response_pd

    def get_solar_forecast_cloudmove(self) -> pd.DataFrame:
        """
        TODO
        """
        variables = {
            'action': 'getforecast_cloudmove',
            'format': self.format
        }
        response = self._send_get_request(variables)
        response_dict = response.json()

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
        