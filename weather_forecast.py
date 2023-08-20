import requests
import pandas as pd

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
        # initially all fix points calling site_add + add only if not already existing
        # site name in ascending order
        # then introduce online position and look some km ahead in the direction of the road (needed roate lat and long)
        pass
    
    def check_variables(self, variables) -> None:
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

                if not isinstance(value, value_type):
                    raise ValueError(f'{variable} has to be a {value_type}. Received: {value}')

                if min_value is not None and max_value is not None:
                    if not (min_value <= value <= max_value):
                        raise ValueError(f'{variable} has to be between {min_value} and {max_value}. Received: {value}')
            else:
                raise ValueError(f'Wrong variable. Received: {variable}')
                    
    def send_get_request(self, variables):
        self.check_variables(variables)

        mdx_url = f'{self.api_website}key={self.key}&service={self.service}'
        for key, value in variables.items():
            mdx_url += f'&{key}={value}'

        payload = {}
        headers = {}
        response = requests.request("GET", mdx_url, headers=headers, data=payload)
        return response

    def get_site_add(self, name, latitude, longitude, azimuth=0, inclination=0) -> None:
        # initially only one by one, then with a vector of positions received as input

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
        print(response.text)

    def get_site_edit(self, site_id, **kwargs) -> None:
        # initially only one by one, then with a vector of positions received as input

        variables = { # altitude, horizon, hddctin, hddctout, and cddctout are not included
            'action': 'siteedit',
            'site_id': site_id
        }

        # TODO lat e lon insieme per forza
        # e chiama check_variables

        response = self.send_get_request(variables)
        print(response.text)

    def get_site_delete(self, site_id) -> None:
        # initially only one by one, then with a vector of positions received as input

        variables = {
            'action': 'sitedelete',
            'site_id': site_id
        }

        response = self.send_get_request(variables)
        print(response.text)

    def get_site_info(self) -> None:
        variables = {
            'action': 'siteinfo',
            'format': self.format
        }

        response = self.send_get_request(variables)
        print(response.text)

    def get_site_id(self, name):
        #TODO get site id from name of a site
        # improve that a full response is given and name (from 1 to 100) is attributed with site id
        pass

    def get_solar_forecast(self) -> None:
        variables = {
            'action': 'getforecast',
            'format': self.format
        }

        response = self.send_get_request(variables)
        print(response.text)

        # Extract values from the JSON data
        values_list = []
        for item in response:
            value1 = item.get("gk")
            value2 = item.get("tcc")
            values_list.append((value1, value2))

        # Create a DataFrame from the extracted values
        df = pd.DataFrame(values_list, columns=["Column1", "Column2"])

        # Display the DataFrame
        print(df)

    def save_raw_data():
        # save data in 2D matrix space time in pandas
        pass