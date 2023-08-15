import requests

mdx_key = 'FA8F60A1A6F5D9254DD8E1D3566E7C30'
mdx_key = '54F773F38E50F4CF562384A44B9948D3'

mdx_url = ('https://mdx.meteotest.ch/api_v1?key={key}&service=solarforecast'
           '&action=siteadd&latitude=47.2&longitude=7.2&inclination=30'
           '&azimuth=180&format=json&name=StrategyWeatherDataForecasts'.format(key=mdx_key))

r = requests.get(mdx_url)
result = r.json()
# if it worked, variable 'result' contains details of
# created site. Otherwise 'result' contains an
# error message.

if r.status_code == 200:
  print("It worked!")
else:
  print("An error occurred:")
  # let's check what the problem is...
  print(result)