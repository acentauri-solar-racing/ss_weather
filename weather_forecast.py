import requests
import json
import pandas as pd
from bs4 import BeautifulSoup

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
                if variable == 'site_id':
                    response = self.get_site_info(print_is_requested=False)
                    response_dict = response.json()
                    
                    sites_id = response_dict["payload"]["solarforecast"]["sites"].keys()
                    if str(value) not in set(sites_id):
                        raise ValueError(f'Site ID {value} is not valid.')
            
    def _check_response(self, response:requests.models.Response) -> None:
        content_type = response.headers.get('Content-Type')

        # TODO RECEIVE THE ACTION AND PRINT ALSO FROM WHERE IT WAS CALLED

        if 'application/json' in content_type:
            response_dict = response.json() # equivalent to = json.loads(response.text)
            print(f'Response status: {response_dict["status"]}')

        elif 'text/html' in content_type:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find the <div> with class "alert alert-info" and get its text
            info_div = soup.find('div', class_='alert alert-info')
            if info_div:
                status_text = info_div.get_text().strip()
                print(f'Response status: {status_text}')

        else:
            print('Unknown content type')
            
    def _send_get_request(self, variables:dict) -> requests.models.Response:
        self._check_variables(variables)

        mdx_url = f'{self.api_website}key={self.key}&service={self.service}'
        for key, value in variables.items():
            mdx_url += f'&{key}={value}'

        response = requests.get(mdx_url)

        self._check_response(response)
        return response

    def get_site_add(self, name:str, latitude:float, longitude:float, azimuth:int=0, inclination:int=0, print_is_requested:bool=True) -> None:
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

    def get_site_edit(self, site_id:int, **kwargs) -> None:
        variables = { # altitude, horizon, hddctin, hddctout, and cddctout are not included
            'action': 'siteedit',
            'site_id': site_id
        }

        # TODO lat e lon insieme per forza
        # e chiama check_variables

        response = self._send_get_request(variables)

    def get_site_delete(self, site_id:int, print_is_requested:bool=True) -> None:
        variables = {
            'action': 'sitedelete',
            'site_id': site_id
        }
        self._send_get_request(variables)

        # Update self.forecast_sites by removing the corresponding row
        self.forecast_sites = self.forecast_sites[self.forecast_sites['site_id'] != site_id]

        if print_is_requested:
            print(f'Site with id {site_id} has been removed.')

    def delete_all_sites(self, print_is_requested:bool=True) -> None:
        for _, row in self.forecast_sites.iterrows():
            site_id = row['site_id']
            self.get_site_delete(site_id, print_is_requested=print_is_requested)
        
        if print_is_requested:
            print("All sites have been deleted.")
            print(self.forecast_sites)

    def get_site_info(self, print_is_requested:bool=True) -> requests.models.Response:
        variables = {
            'action': 'siteinfo',
            'format': self.format
        }
        response = self._send_get_request(variables)

        if print_is_requested:
            print(json.dumps(response.text, indent=2)) # TODO CORRECT THIS PRINT AS IT WAS BEFORE
        return response

    def get_solar_forecast(self) -> None:
        variables = {
            'action': 'getforecast',
            'format': self.format
        }
        response = self._send_get_request(variables)

    def get_solar_forecast_cloudmove(self) -> None:
        variables = {
            'action': 'getforecast_cloudmove',
            'format': self.format
        }
        response = self._send_get_request(variables)

    def save_raw_data() -> None:
        # save data in 3D matrix space-time+variable in pandas
        pass