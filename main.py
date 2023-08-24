import pandas as pd
import numpy as np

from route import Route
from weather_forecast import WeatherForecast

current_position = {'longitude': 130.868566,
                    'latitude': -12.432466}
delta_spacing = 100000.0 # in meters
number_sites = 3

route = Route()
# route.get_final_data(current_position)
# route.get_final_data(current_position, delta_spacing=delta_spacing)
dataframe = route.get_route_data(current_position, number_sites=number_sites)

api = WeatherForecast()
api.add_sites(dataframe)
api.get_site_edit(584858, True, name="cc")
# api.delete_all_sites()