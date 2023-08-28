import requests
import pandas as pd
import CONSTANTS as costants
from api_parser import ApiParser

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

    def __init__(self, parser:ApiParser) -> None:
        self.parser = parser
        self.column_names = costants.API_COLUMN_NAMES
        self.forecast_sites = pd.DataFrame(columns=self.column_names)

        dataframe = self.get_site_info(print_is_requested=False)

        self.forecast_sites = pd.concat([self.forecast_sites, dataframe], ignore_index=True)

        print(f"Current sites' info has been retrieved. \n {self.forecast_sites}")
    
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
                
                # TODO check post request

                # Check site id
                # TODO FIND BETTER SEARCH ALGORITHM THAT CHECKS IF THE SITE ID IS PRESENT IN SELF.FORECAST_SITES
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
    
    def _send_post_request(self, variables:dict) -> requests.models.Response:
        """
        Format the URL and send a POST request.
        """
        self._check_variables(variables)

        # TODO

        url = "https://mdx.meteotest.ch/api_v1"

        payload = {'key': self.KEY,
        'service': self.SERVICE,
        'format': self.FORMAT,
        'action': 'add_measurements',
        'measurements': '{584990: {"2023-08-27 14:00:00": {"gh": 230},"2023-08-27 14:15:00": {"gh": 220}}}'}
        files=[

        ]
        headers = {}

        response = requests.request("POST", url, headers=headers, data=payload, files=files)

        print(response.text)

        mdx_url = f'{self.API_WEBSITE}key={self.KEY}&service={self.SERVICE}&format={self.FORMAT}'
        for key, value in variables.items():
            mdx_url += f'&{key}={value}'

        response = requests.post(mdx_url, timeout=10)

        return response
    
    def post_add_measurement(self, site_id:int, dataframe:pd.DataFrame, print_is_requested:bool=True) -> None:
        """
        TODO
        """
        # Check if dataframe is a Pandas DataFrame
        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError('dataframe must be a Pandas DataFrame.')
        
        # Check if dataframe has the correct columns
        column_names = ['SITE_ID', 'TIMESTAMP', 'GH']
        if not set(dataframe.columns) == set(column_names):
            raise ValueError(f"dataframe columns must be {self.column_names}. Received: {dataframe.columns}")
        
        # Call parser
        json_data = self.parser.parse_add_measurement_dataframe(dataframe=dataframe, function_tag='add_measurements')

        # json_data = {
        #         SITE-ID: {
        #             "2021-06-11 05:00:00": {
        #                 "gh": 58
        #             },
        #             "2021-06-11 05:15:00": {
        #                 "gh": 219
        #             },
        #             "2021-06-11 05:30:00": {
        #                 "gh": 369
        #             },
        #             ...
        #         },
        #         SITE-ID: {
        #             ...
        #         }
        # }
        # {584990: {"2023-08-26 09:15:00": {"gh": 620},"2023-08-26 09:30:00": {"gh": 624},"2023-08-26 09:45:00": {"gh": 605}}}

        variables = {
            'action': 'add_measurements',
            'measurements': json_data
        }
        response = self._send_post_request(variables)

        # Parser not needed, because the response is not interesting

        if print_is_requested:
            print(f"Measurements for site {site_id} has been added.")

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
        response_df = self.parser.parse_site_add_response(response, function_tag=variables['action'])

        # Add the new site to the forecast_sites DataFrame
        self._modify_site_add_data(dataframe=response_df, print_is_requested=print_is_requested)

        if print_is_requested:
            print(f'Site with name {name} has been added in the API.')

    def get_site_edit(self, site_id:int, print_is_requested:bool=True, **kwargs) -> None:
        """
        Edit name or position (longitude and latitude)
        """
        variables = {
            'action': 'siteedit',
            'site_id': site_id
        }
        string = ""
        correct_kwargs:bool = False

        # Check if kwargs contains 'name' or 'position'
        if 'name' in kwargs:
            variables['name'] = kwargs['name']
            string += f"New name: {kwargs['name']}. "
            correct_kwargs = True

        if 'position' in kwargs:
            position = kwargs['position']

            # Check if position is a dictionary with 'longitude' and 'latitude' keys
            if isinstance(position, dict) and 'longitude' in position and 'latitude' in position:
                variables['longitude'] = position['longitude']
                variables['latitude'] = position['latitude']
                string += f"New position: {kwargs['position']}. "
                correct_kwargs = True
            else:
                raise ValueError("Position should be a dictionary with 'longitude' and 'latitude' keys.")
        
        if not correct_kwargs:
            print_is_requested = False
            print("Nothing to edit.")

        self._send_get_request(variables)

        # Parser not needed, because the response is not interesting
        
        # Edit the new site to the forecast_sites DataFrame
        self._modify_site_edit_data(site_id=site_id, print_is_requested=False, **kwargs)

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

        # Parser not needed, because the response is not interesting

        # Delete the new site to the forecast_sites DataFrame
        self._modify_site_delete_data(site_id=site_id, print_is_requested=False)

        if print_is_requested:
            print(f'Site with id {site_id} has been removed.')

    def get_site_info(self, print_is_requested:bool=True) -> pd.DataFrame:
        """
        TODO
        """
        variables = {
            'action': 'siteinfo',
            'format': self.FORMAT
        }
        response = self._send_get_request(variables)

        # Parse the response
        response_df, response_formatted = self.parser.parse_site_info_response(response, function_tag=variables['action'])

        if print_is_requested:
            print(f"Site information have been retrieved: \n {response_formatted}")

        return response_df

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
        response_df = self.parser.parse_solar_forecast_response(response, function_tag=variables['action'])

        if print_is_requested:
            print("Solar forecast have been retrieved.")

        return response_df

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
        response_pd = self.parser.parse_solar_forecast_cloudmove_response(response, function_tag=variables['action'])

        if print_is_requested:
            print("Solar forecast CloudMove have been retrieved.")

        return response_pd   
    
    def _modify_site_add_data(self, dataframe:pd.DataFrame, print_is_requested:bool=True) -> None:
        """
        TODO
        """
        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError('dataframe must be a Pandas DataFrame.')
        
        # Update the forecast_sites DataFrame
        self.forecast_sites = pd.concat([self.forecast_sites, dataframe], ignore_index=True)

        if print_is_requested:
            print(f"Add site has been saved: \n {self.forecast_sites}")

    def _modify_site_edit_data(self, site_id:int, print_is_requested:bool=True, **kwargs) -> None:
        """
        TODO
        """
        # Update the forecast_sites DataFrame
        if 'name' in kwargs:
            self.forecast_sites.loc[self.forecast_sites['site_id'] == site_id, 'name'] = kwargs['name']
        
        if 'position' in kwargs:
            position = kwargs['position']
            self.forecast_sites.loc[self.forecast_sites['site_id'] == site_id, 'longitude'] = position['longitude']
            self.forecast_sites.loc[self.forecast_sites['site_id'] == site_id, 'latitude'] = position['latitude']

        if print_is_requested:
            print(f"Edit site has been saved: \n {self.forecast_sites}.")

    def _modify_site_delete_data(self, site_id:int, print_is_requested:bool=True) -> None:
        """
        TODO
        """
        # Update the forecast_sites DataFrame
        self.forecast_sites = self.forecast_sites[self.forecast_sites['site_id'] != site_id]

        if print_is_requested:
            print(f"Delete site has been saved: \n {self.forecast_sites}.")