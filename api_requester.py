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
    KEY: str = '6C985B9DF101FF63EB494A0FF420FCA6' # TODO MOVE THIS KEY TO A SAFER PLACE
    SERVICE: str = 'solarforecast'
    FORMAT: str = 'json'

    def __init__(self, parser:ApiParser, print_is_requested:bool=True) -> None:
        self.parser = parser
        self.column_names = costants.API_COLUMN_NAMES

        dataframe = self.get_site_info(print_is_requested=False)
        self.forecast_sites = pd.DataFrame(dataframe, columns=self.column_names)

        if print_is_requested:
            print(f"Current sites' info has been retrieved. \n {self.forecast_sites}")
    
    def _check_variables(self, variables:dict) -> None:
        """
        Check if the variables are of the correct type and between the ranges.
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
            raise ValueError(f"dataframe columns must be {column_names}. Received: {dataframe.columns}")
        
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
        self.forecast_sites = pd.concat([self.forecast_sites, response_df])

        if print_is_requested:
            print(f'Site with name {name} has been added. \n {self.forecast_sites}')

    def get_site_edit(self, site_id:int, print_is_requested:bool=True, **kwargs) -> None:
        """
        Edit name or position (longitude and latitude)
        """
        variables = {
            'action': 'siteedit',
            'format': self.FORMAT,
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
        if 'name' in kwargs:
            self.forecast_sites.at[site_id, 'name'] = kwargs['name']

        if 'position' in kwargs:
            position = kwargs['position']
            self.forecast_sites.at[site_id, 'longitude'] = position['longitude']
            self.forecast_sites.at[site_id, 'latitude'] = position['latitude']

        if print_is_requested:
            print(f"Edit site has been saved: \n {self.forecast_sites}.")

        if print_is_requested:
            print(f"Site with id {site_id} has been edited: {string}")

    def get_site_delete(self, site_id:int, print_is_requested:bool=True) -> None:
        """
        TODO
        """
        variables = {
            'action': 'sitedelete',
            'format': self.FORMAT,
            'site_id': site_id
        }
        self._send_get_request(variables)

        # Parser not needed, because the response is not interesting

        # Delete the new site to the forecast_sites DataFrame
        self.forecast_sites.drop(site_id, inplace=True)

        if print_is_requested:
            print(f'Site with id {site_id} has been removed. \n {self.forecast_sites}')

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
        # TODO SITE ID CONVERT TO POSITION?

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
        response_pd = self.parser.parse_solar_forecast_response(response, function_tag=variables['action'])

        if print_is_requested:
            print("Solar forecast CloudMove have been retrieved.")

        return response_pd