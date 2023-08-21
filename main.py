import pandas as pd
import numpy as np

from route import Route
from weather_forecast import WeatherForecast

current_position = {'longitude': 130.868566,
                    'latitude': -12.432466}
delta_spacing = 100000 # in meters

route = Route()
route.get_final_data(current_position)
route.get_final_data(current_position, delta_spacing)