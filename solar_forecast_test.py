from weather_forecast import WeatherForecast

api = WeatherForecast()

# api.get_site_add(name='Adelaide', latitude=-34.89559537640413, longitude=138.5987843819972)
# api.get_site_edit(site_id=584561)
# api.get_site_delete(site_id=584526)
api.get_solar_forecast()
# api.get_site_info()

# # Example usage:
# latitude = 45.1234
# longitude = 13.621
# azimuth = 190
# inclination = 30
# name = 'My PV'