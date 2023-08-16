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

    def create_request_url(self, ):
        url: str = self.api_website

        return url

    def get_site_add(self, ):
        # initially only one by one, then with a vector of positions received or saved here
        action: str = 'siteadd'
        

"https://mdx.meteotest.ch/api_v1?key=54F773F38E50F4CF562384A44B9948D3&service=solarforecast&action=siteadd&format=json&name=testDarwin&latitude=-12.39828502488282&longitude=130.88590799669225&inclination=0"

payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

        pass

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