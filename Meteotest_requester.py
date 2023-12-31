# Created by Giacomo Mastroddi August 2023

import requests
import constants
import pandas as pd
from typing import Tuple
from dateutil.tz import tzlocal
from Meteotest_parser import MeteotestParser

class MeteotestRequester():
    """ Class for interacting with the weather forecast API from Meteotest.

    Attributes:
        website (str): The base API URL.
        key (str): The API key for authentication.
        service (str): The service to be used.
        format (str): The response format (default: 'json').
        timeout (int): The timeout for the request (default: 10)."""
        
    WEBSITE: str = 'https://mdx.meteotest.ch/api_v1'
    KEY: str = constants.KEY_METEOTEST
    SERVICE: str = 'solarforecast'
    FORMAT: str = 'json'
    TIMEOUT: int = 10

    def __init__(self, parser:MeteotestParser, print_is_requested:bool=False) -> None:
        self.parser = parser
        self.forecast_sites = self.get_site_info()

        self.previous_SF_df = pd.DataFrame()
        self.previous_SF_time: pd.Timestamp = pd.NaT
        self.previous_CM_df = pd.DataFrame()
        self.previous_CM_time: pd.Timestamp = pd.NaT

        if print_is_requested:
            print("Current sites' info has been retrieved:")
            self.print_current_sites

    @property
    def print_current_sites(self) -> None:
        """ Print the current sites' info."""
        print(self.forecast_sites)

    @property
    def get_current_sites(self) -> pd.DataFrame:
        """ Return the current sites' info."""
        return self.forecast_sites
    
    def _check_variables(self, variables:dict) -> None:
        """ Check if the variables are of the correct type and between the ranges. 
        
            Inputs:
                variables (dict): The variables to be checked. """

        validation_rules = { # horizon, hddctin, hddctout, and cddctout are not included
            'site_id': (int, None, None),
            'name': (str, None, None),
            'action': (str, None, None),
            'format': (str, None, None),
            'latitude': (float, constants.GEO['latitude']['min'], constants.GEO['latitude']['max']),
            'longitude': (float, constants.GEO['longitude']['min'], constants.GEO['longitude']['max']),
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
                if variable == 'site_id':
                    indices = self.forecast_sites.index
                    if value not in indices:
                        raise ValueError(f'{variable} has to be one of {indices}. Received: {value}')
    
    def _send_get_request(self, variables:dict) -> Tuple[requests.models.Response, bool]:
        """ Format the URL and send a GET request to the API. 
        
        Inputs:
            variables (dict): The variables to be sent to the API. """

        self._check_variables(variables)

        mdx_url = f'{self.WEBSITE}?key={self.KEY}&service={self.SERVICE}&format={self.FORMAT}'
        for key, value in variables.items():
            mdx_url += f'&{key}={value}'

        try:
            response = requests.get(url=mdx_url, timeout=self.TIMEOUT)
            return response, True
        
        except (requests.ConnectionError, requests.Timeout):
            print("No internet connection or the connection timed out.")
            return None, False
    
    def _send_post_request(self, variables:dict) -> Tuple[requests.models.Response, bool]:
        """ Send a POST request.
        
        Inputs:
            variables (dict): The variables to be sent to the API. """
        
        try:
            response = requests.post(url=self.WEBSITE, data=variables, timeout=self.TIMEOUT)
            return response, True
        
        except requests.ConnectionError or requests.ConnectTimeout:
            print("No internet connection.")
            return None, False
    
    def post_add_measurement(self, gh_df:pd.DataFrame, print_is_requested:bool=False) -> None:
        """ Call the API to post the irradiance measurements.

            Inputs:
                gh_df (pd.DataFrame): The irradiance dataframe with site id and time as index and global irradiance (gh) as columns. """
        
        # Convert the irradiance dataframe to dictionary
        gh_dict = {
            site_id: {
                time: {"gh": row['gh']} for time, row in group.iterrows()
            }
            for site_id, group in gh_df.groupby(level='site_id')
        }

        variables = {
            'key': self.KEY,
            'service': self.SERVICE,
            'format': self.FORMAT,
            'action': 'add_measurements',
            'measurements': str(gh_dict)
        }
        response, internet_on = self._send_post_request(variables)

        # TODO CHECK POST RESPONSE

        if not internet_on:
            return
        
        # Parser not needed, because the response is not interesting

        if print_is_requested:
            print('Measurements have been sent.')

    def get_site_add(self, name:str, latitude:float, longitude:float, azimuth:int=0, inclination:int=0, print_is_requested:bool=False) -> None:
        """ Call the API to add a new site given the inputs. 
        
            Inputs:
                name (str): The name of the site.
                latitude (float): The latitude of the site.
                longitude (float): The longitude of the site.
                azimuth (int): The azimuth of the site (default: 0).
                inclination (int): The inclination of the site (default: 0).
                print_is_requested (bool): Whether to print the result (default: True). """

        variables = { # altitude, horizon, hddctin, hddctout, and cddctout are not included
            'action': 'siteadd',
            'name': name,
            'latitude': latitude,
            'longitude': longitude,
            'azimuth': azimuth,
            'inclination': inclination
        }
        response, internet_on = self._send_get_request(variables)

        if not internet_on:
            return
        
        # Extract the required information from response_dict
        response_df = self.parser.parse_site_add_response(response, function_tag=variables['action'])

        # Add the new site to the forecast_sites DataFrame
        self.forecast_sites = pd.concat([self.forecast_sites, response_df])

        if print_is_requested:
            print(f'Site with name {name} has been added.')

    def get_site_edit(self, site_id:int, print_is_requested:bool=False, **kwargs) -> None:
        """ Edit name or position (longitude and latitude).
        
            Inputs:
                site_id (int): The id of the site to be edited.
                print_is_requested (bool): Whether to print the result (default: True).
                **kwargs: The keyword arguments to be edited:
                    name (str): The new name of the site.
                    position (dict): The new position of the site with 'longitude' and 'latitude' keys. """
        
        variables = {
            'action': 'siteedit',
            'site_id': site_id
        }
        string = ""
        correct_kwargs:bool = False

        # Check if kwargs contains 'name'
        if 'name' in kwargs:
            name = kwargs['name']

            # Check if name is not None, a string, and not empty
            if name is None and not isinstance(name, str) and name == '':
                raise ValueError("Name should be a non-empty string.")
            else:
                # Assign the new name to the variables to be sent
                variables['name'] = name
                string += f"New name: {name}. "
                correct_kwargs = True
                
        # Check if kwargs contains 'position'
        if 'position' in kwargs:
            position = kwargs['position']

            # Check if position is not None, a dictionary with 'longitude' and 'latitude' keys
            if position is None and not isinstance(position, dict) and 'longitude' not in position and 'latitude' not in position:
                raise ValueError("Position should be a dictionary with 'longitude' and 'latitude' keys.")
            else:
                # Check if longitude and latitude are of different type
                if not isinstance(position['longitude'], type(position['latitude'])):
                    raise ValueError("Longitude and latitude must be of the same type.")
                
                # Check if longitude and latitude are not NaN
                if pd.isna(position['longitude']) or pd.isna(position['latitude']):
                    raise ValueError("Longitude and latitude cannot be NaN.")

                variables['longitude'] = position['longitude']
                variables['latitude'] = position['latitude']
                string += f"New position: Longitude: {position['longitude']}, latitude: {position['latitude']}. "
                correct_kwargs = True
        
        if not correct_kwargs:
            print_is_requested = False
            print("Nothing to edit.")
            return

        _, internet_on = self._send_get_request(variables)

        if not internet_on:
            return
        
        # Parser not needed, because the response is not interesting
        
        # Edit the new site to the forecast_sites DataFrame
        if 'name' in kwargs:
            self.forecast_sites.at[site_id, 'name'] = kwargs['name']

        if 'position' in kwargs:
            position = kwargs['position']
            self.forecast_sites.at[site_id, 'longitude'] = position['longitude']
            self.forecast_sites.at[site_id, 'latitude'] = position['latitude']

        if print_is_requested:
            print(f'Site with id {site_id} has been edited: {string} \n {self.forecast_sites.at[site_id]}')

    def get_site_delete(self, site_id:int, print_is_requested:bool=False) -> None:
        """ Call the API to delete a site given the id.

            Inputs:
                site_id (int): The id of the site to be deleted.
                print_is_requested (bool): Whether to print the result (default: True). """
        
        variables = {
            'action': 'sitedelete',
            'site_id': site_id
        }
        _, internet_on = self._send_get_request(variables)
        
        if not internet_on:
            return

        # Parser not needed, because the response is not interesting

        # Delete the new site to the forecast_sites DataFrame
        self.forecast_sites.drop(site_id, inplace=True)

        if print_is_requested:
            print(f'Site with id {site_id} has been removed.')

    def get_site_info(self, print_is_requested:bool=False) -> pd.DataFrame:
        """ Call the API to get the information of all sites.

            Inputs:
                print_is_requested (bool): Whether to print the result (default: True). """
        
        variables = {'action': 'siteinfo'}

        response, internet_on = self._send_get_request(variables)

        if not internet_on:
            return

        # Parse the response
        response_df, response_formatted = self.parser.parse_site_info_response(response, function_tag=variables['action'])

        if print_is_requested:
            print(f"Site information have been retrieved: \n {response_formatted}")

        return response_df
    
    @property
    def get_solar_forecast_last_time(self) -> pd.Timestamp:
        """ Return the time of the last solar forecast. """
        return self.previous_SF_time

    def get_solar_forecast(self, print_is_requested:bool=False) -> pd.DataFrame:
        """ Call the API to get the solar forecast for the next 72 hours.

            Inputs:
                print_is_requested (bool): Whether to print the result (default: True). """
        
        variables = {'action': 'getforecast'}

        response, internet_on = self._send_get_request(variables)

        if not internet_on:
            return
        
        # Parse the response
        response_df = self.parser.parse_solar_forecast_response(response, self.forecast_sites, function_tag=variables['action'])

        local_tz = tzlocal()
        self.previous_SF_time = pd.Timestamp.now(tz=local_tz)
        
        if not response_df.empty:
            self.previous_SF_df = response_df
        
        if print_is_requested:
            print("Solar forecast have been retrieved.")

        return response_df
    
    @property
    def get_solar_forecast_cloudmove_last_time(self) -> pd.Timestamp:
        """ Return the time of the last CloudMove solar forecast. """
        return self.previous_CM_time

    def get_solar_forecast_cloudmove(self, print_is_requested:bool=False) -> pd.DataFrame:
        """ Call the API to get the CloudMove forecast for the next 6 hours.

            Inputs:
                print_is_requested (bool): Whether to print the result (default: True). """
        
        variables = {'action': 'getforecast_cloudmove'}

        response, internet_on = self._send_get_request(variables)

        if not internet_on:
            return
        
        # Parse the response
        response_df = self.parser.parse_solar_forecast_response(response, self.forecast_sites, function_tag=variables['action'])

        local_tz = tzlocal()
        self.previous_CM_time = pd.Timestamp.now(tz=local_tz)

        if not response_df.empty:
            self.previous_CM_df = response_df

        if print_is_requested:
            print("Solar forecast CloudMove have been retrieved.")

        return response_df