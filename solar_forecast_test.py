import requests
import time

def get_request(mdx_url):
  r = requests.get(mdx_url)
  result = r.json()

  if r.status_code == 200:
    print("forecast data:")
    print(result)
  else:
    print("An error occurred:")
    print(result)
  
  time.sleep(4)

mdx_key = 'FA8F60A1A6F5D9254DD8E1D3566E7C30'
mdx_key = '54F773F38E50F4CF562384A44B9948D3'

mdx_url = ('https://mdx.meteotest.ch/api_v1?key={key}&service=solarforecast'
           '&action=siteadd&latitude=47.2&longitude=7.2&inclination=30'
           '&azimuth=180&format=json&name=test1'.format(key=mdx_key))
print(mdx_url)

get_request(mdx_url)

mdx_url = ('https://mdx.meteotest.ch/api_v1?key={key}&service=solarforecast'
           '&action=getforecast&format=json&name=StrategyWeatherDataForecasts'.format(key=mdx_key))

get_request(mdx_url)

#######################################33

def get_mdx_forecast_data(mdx_key, latitude, longitude, azimuth, inclination, name):
    base_url = 'https://mdx.meteotest.ch/api_v1'
    params = {
        'key': mdx_key,
        'service': 'solarforecast',
        'action': 'siteadd',
        'name': name,
        'latitude': latitude,
        'longitude': longitude,
        'azimuth': azimuth,
        'inclination': inclination
    }

    mdx_url = f'{base_url}?{requests.compat.urlencode(params)}'

    print(mdx_url)

    r = requests.get(mdx_url)
    # result = r.json()

    if r.status_code == 200:
        print("forecast data:")
        print(result)
    else:
        print("An error occurred:")
        # let's check what the problem is...
        print(result)

# Example usage:
latitude = 45.1234
longitude = 13.621
azimuth = 190
inclination = 30
name = 'My PV site 123'

get_mdx_forecast_data(mdx_key, latitude, longitude, azimuth, inclination, name)
