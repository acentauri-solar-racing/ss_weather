import requests
import pandas as pd
from api_parser import Parser

class ApiRequester():
    """
    Class for interacting with the weather forecast API from Meteotest.

    Attributes:
        api_website (str): The base API URL.
        key (str): The API key for authentication.
        service (str): The service to be used.
        format (str): The response format (default: 'json').
    """
        
    API_WEBSITE: str = 'https://mdx.meteotest.ch/api_v1?'
    KEY: str = '54F773F38E50F4CF562384A44B9948D3'
    SERVICE: str = 'solarforecast'
    FORMAT: str = 'json'

    def __init__(self) -> None:

        # TODO DOVE SPOSTARE QUESTO?

        self.column_names = ['name', 'site_id', 'longitude', 'latitude', 'altitude']
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
                altitude_extracted = site_info['altitude']

                extracted_values = [[name_extracted, int(site_id), longitude_extracted, latitude_extracted, altitude_extracted]]
                extracted_values_pd = pd.DataFrame(extracted_values, columns=self.column_names)

                self.forecast_sites = pd.concat([self.forecast_sites, extracted_values_pd], ignore_index=True)

        print(f"Current sites saved at Meteotest: \n, {self.forecast_sites}")
    
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
                # TODO SPOSTARE QUESTO CHE FA IL CHECK NEL PANDAS SALVATO FUORI DA QUESTA CLASSE DEL SELF
                # if variable == 'site_id':
                    # response = self.get_site_info(print_is_requested=False)
                    # response_dict = response.json()
                    
                    # sites_id = response_dict["payload"]["solarforecast"]["sites"].keys()
                    # if str(value) not in set(sites_id):
                    #     raise ValueError(f'Site ID {value} is not valid.')
            
    def _send_get_request(self, variables:dict) -> requests.models.Response:
        """
        Format the URL and send a GET request.
        """
        self._check_variables(variables)

        mdx_url = f'{self.API_WEBSITE}key={self.KEY}&service={self.SERVICE}'
        for key, value in variables.items():
            mdx_url += f'&{key}={value}'

        response = requests.get(mdx_url, timeout=10)

        return response

    def get_site_add(self, name:str, latitude:float, longitude:float, azimuth:int=0, inclination:int=0, print_is_requested:bool=True) -> None:
        """
        Call the API to add a new site.
        """
        variables = { # altitude, horizon, hddctin, hddctout, and cddctout are not included
            'action': 'siteadd',
            'format': self.FORMAT,
            'name': name,
            'latitude': latitude,
            'longitude': longitude,
            'azimuth': azimuth,
            'inclination': inclination
        }
        response = self._send_get_request(variables)

        # Extract the required information from response_dict
        response_df = Parser.parse_site_add_response(response, function_tag=variables["action"])

        # Add the new site to the forecast_sites DataFrame
        self.forecast_sites = pd.concat([self.forecast_sites, response_df], ignore_index=True)

        if print_is_requested:
            print(f'Site with name {name} has been added.')

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

            # Check if position is a dictionary with 'longitude' and 'latitude' keys
            if isinstance(position, dict) and 'longitude' in position and 'latitude' in position:
                variables['longitude'] = position['longitude']
                variables['latitude'] = position['latitude']
                string += f"New position: {kwargs['position']}. "
            else:
                raise ValueError("Position should be a dictionary with 'longitude' and 'latitude' keys.")

        self._send_get_request(variables)

        # Update the forecast_sites DataFrame
        if 'name' in kwargs:
            self.forecast_sites.loc[self.forecast_sites['site_id'] == site_id, 'name'] = kwargs['name']
        
        if 'position' in kwargs:
            self.forecast_sites.loc[self.forecast_sites['site_id'] == site_id, 'longitude'] = position['longitude']
            self.forecast_sites.loc[self.forecast_sites['site_id'] == site_id, 'latitude'] = position['latitude']

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

        # Update the forecast_sites DataFrame
        self.forecast_sites = self.forecast_sites[self.forecast_sites['site_id'] != site_id]

        if print_is_requested:
            print(f'Site with id {site_id} has been removed.')

    def get_site_info(self, print_is_requested:bool=True) -> requests.models.Response: # TODO FARLO PANDAS GIA QUI?
        """
        TODO
        """
        variables = {
            'action': 'siteinfo',
            'format': self.FORMAT
        }
        response = self._send_get_request(variables)

        # Parse the response
        response_formatted = Parser.parse_site_info_response(response)

        if print_is_requested:
            print(f"Site information have been retrieved. \n {response_formatted}")

        return response

    def get_solar_forecast(self, print_is_requested:bool=True) -> pd.DataFrame:
        """
        TODO
        """
        variables = {
            'action': 'getforecast',
            'format': self.FORMAT
        }
        response = self._send_get_request(variables)
        
        # Parse the response
        response_pd = Parser.parse_solar_forecast_response(response)

        if print_is_requested:
            print("Solar forecast have been retrieved.")

        return response_pd

    def get_solar_forecast_cloudmove(self, print_is_requested:bool=True) -> pd.DataFrame:
        """
        TODO
        """
        variables = {
            'action': 'getforecast_cloudmove',
            'format': self.FORMAT
        }
        response = self._send_get_request(variables)

        # Parse the response
        response_pd = Parser.parse_solar_forecast_cloudmove_response(response)

        if print_is_requested:
            print("Solar forecast cloudmove have been retrieved.")

        return response_pd