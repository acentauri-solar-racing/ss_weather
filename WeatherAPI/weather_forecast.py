import requests
import pandas as pd

class WeatherForecast():
    api_website: str = 'https://mdx.meteotest.ch/api_v1?'
    key: str = '54F773F38E50F4CF562384A44B9948D3'
    service: str = 'solarforecast'
    format: str = 'json'

    def __init__(self) -> None:
        # initially all fix points calling site_add + add only if not already existing
        # site name in ascending order
        # then introduce online position and look some km ahead in the direction of the road (needed roate lat and long)
        pass

    # TODO UTC timezone check

    def create_request_url(self, **kwargs):
        # to remove this function
        url = f'{self.api_website}key={self.key}&service={self.service}&format={self.format}'

        for key, value in kwargs.items():
            url += f'&{key}={value}'

        return url
    
    def check_variables(self, **kwargs):
        validation_rules = { # horizon, hddctin, hddctout, and cddctout are not included
            'site_id': (int, None, None),
            'name': (str, None, None),
            'latitude': (float, -90.0, 90.0),
            'longitude': (float, -180.0, 180.0),
            'azimuth': (int, 0, 360),
            'inclination': (int, 0, 90),
            'altitude': (int, None, None)
        }

        for key, value in kwargs.items():
            if key in validation_rules:
                value_type, min_value, max_value = validation_rules[key]

                if not isinstance(value, value_type):
                    raise ValueError(f'{key} has to be a {value_type}. Received: {value}')

                if min_value is not None and max_value is not None:
                    if not (min_value <= value <= max_value):
                        raise ValueError(f'{key} has to be between {min_value} and {max_value}. Received: {value}')

    def get_site_add(self, name, latitude, longitude, azimuth=0, inclination=0, **kwargs):
        # initially only one by one, then with a vector of positions received as input
        

        action: str = 'siteadd'

        url = f'{self.api_website}key={self.key}&service={self.service}&action={action}&format={self.format}'
        

        "https://mdx.meteotest.ch/api_v1?key=54F773F38E50F4CF562384A44B9948D3&service=solarforecast&action=siteadd&format=json&name=testDarwin&latitude=-12.39828502488282&longitude=130.88590799669225&inclination=0"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response.text)
        requests.get(mdx_url)

    def get_site_delete(self, ):
        action: str = 'sitedelete'
        pass

    def get_site_info(self, ):
        action: str = 'siteinfo'
        pass

    def get_site_edit(self, ):
        action: str = 'siteedit'
        pass

    def get_solar_forecast(self, ):
        action: str = 'getforecast'
        pass

    def get_solar_forecast_cloud_move(self, ):
        pass