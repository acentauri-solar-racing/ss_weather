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
        for site_id, site_info in sites_data.items():
            name_extracted = sites_data[str(site_id)]['name']
            longitude_extracted = sites_data[str(site_id)]['longitude']
            latitude_extracted = sites_data[str(site_id)]['latitude']

            extracted_values = [[name_extracted, site_id, longitude_extracted, latitude_extracted]]
            extracted_values_pd = pd.DataFrame(extracted_values, columns=self.column_names)

            self.forecast_sites = pd.concat([self.forecast_sites, extracted_values_pd], ignore_index=True)
    
    def check_variables(self, variables:dict) -> None:
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
                    
                # Check if the site id is valid
                if variable == 'site_id':
                    response = self.get_site_info(print_is_requested=False)
                    response_dict = response.json()
                    
                    sites_id = response_dict["payload"]["solarforecast"]["sites"].keys()
                    if str(value) not in set(sites_id):
                        raise ValueError(f'Site ID {value} is not valid.')
            
    def check_response(self, response:requests.models.Response) -> None:
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
            
    def send_get_request(self, variables:dict) -> requests.models.Response:
        self.check_variables(variables)

        mdx_url = f'{self.api_website}key={self.key}&service={self.service}'
        for key, value in variables.items():
            mdx_url += f'&{key}={value}'

        response = requests.get(mdx_url)

        self.check_response(response)
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

        response = self.send_get_request(variables)
        response_dict = response.json()

        # Extract the required information from response_dict
        site_id = response_dict['payload']['solarforecast']['sites'][str(name)]['id']
        longitude_extracted = response_dict['payload']['solarforecast']['sites'][str(name)]['longitude']
        latitude_extracted = response_dict['payload']['solarforecast']['sites'][str(name)]['latitude']

        # Extract column names from self.forecast_sites
        column_names = self.forecast_sites.columns

        # Create a new DataFrame with extracted values and assign to corresponding columns
        response_data = [[name, site_id, longitude_extracted, latitude_extracted]]
        response_df = pd.DataFrame(response_data, columns=column_names)

        # Concatenate response_df to forecast_sites
        self.forecast_sites = pd.concat([self.forecast_sites, response_df], ignore_index=True)

        if print_is_requested:
            print(f'Site with name {name} has been added.')

    def get_sites_add(self, dataframe:pd.DataFrame, print_is_requested:bool=True) -> None:
        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError('dataframe must be a Pandas DataFrame.')

        for index, row in dataframe.iterrows():
            name = str(index)
            latitude = row['Latitude']
            longitude = row['Longitude']
            
            # Call get_site_add using the extracted values
            self.get_site_add(name=name, latitude=latitude, longitude=longitude, print_is_requested=print_is_requested)

    def get_site_edit(self, site_id:int, **kwargs) -> None:
        variables = { # altitude, horizon, hddctin, hddctout, and cddctout are not included
            'action': 'siteedit',
            'site_id': site_id
        }

        # TODO lat e lon insieme per forza
        # e chiama check_variables

        response = self.send_get_request(variables)

    def get_site_delete(self, site_id:int, print_is_requested:bool=True) -> None:
        variables = {
            'action': 'sitedelete',
            'site_id': site_id
        }

        self.send_get_request(variables)

        if print_is_requested:
            print(f'Site with id {site_id} has been removed.')

    def get_sites_delete(self, dataframe:pd.DataFrame, delete_all:bool=False, print_is_requested:bool=True) -> None:
        if delete_all:
            print("")
            # delete all sites

    def get_site_info(self, print_is_requested:bool=True) -> requests.models.Response:
        variables = {
            'action': 'siteinfo',
            'format': self.format
        }

        response = self.send_get_request(variables)

        if print_is_requested:
            print(json.dumps(response.text, indent=2)) # TODO CORRECT THIS PRINT AS IT WAS BEFORE

        return response

    def find_site_id(self, name:str) -> int:
        response = self.get_site_info(print_is_requested=False)
        response_dict = response.json()

        sites_data = response_dict["payload"]["solarforecast"]["sites"]
        for site_id, site_info in sites_data.items():
            if site_info["name"] == name:
                print(f"Id of site with name {name}: {site_id}")
                return int(site_id)
            
        print(f"No site found with name: {name}")

    def find_name_id(self, print_is_requested:bool=True) -> None:
        response = self.get_site_info(print_is_requested=False)
        response_dict = response.json()

        sites_data = response_dict["payload"]["solarforecast"]["sites"]
        # TODO expand this for loop
        name_id_dict = {site_data["name"]: site_data["id"] for site_data in sites_data.values()}
        self.name_id_dict = name_id_dict # TODO sfruttare questo self?
        # TODO CHANGE THE STRUCTURE TO PANDAS: NAME, ID, AND THE REST OF INFORMATION

        if print_is_requested:
            print('The list of all name-id for sites:')
            print(name_id_dict)

    def get_solar_forecast(self) -> None:
        variables = {
            'action': 'getforecast',
            'format': self.format
        }

        response = self.send_get_request(variables)

    def get_solar_forecast_cloudmove(self) -> None:
        variables = {
            'action': 'getforecast_cloudmove',
            'format': self.format
        }

        response = self.send_get_request(variables)

    def save_raw_data() -> None:
        # save data in 3D matrix space-time+variable in pandas
        pass

# api = WeatherForecast()
# id = api.find_site_id(name="Darwin")
# api.find_name_id(print_is_requested=True)
# api.get_site_add("testAdd",-12.39828502488282,130.88590799669225)
# api.find_name_id(print_is_requested=True)