import pandas as pd
import numpy as np

from route import Route
from weather_forecast import WeatherForecast

actual_position = {'longitude': 130,
                   'latitude': -12}

delta_spacing = 10000 # in meters

route = Route()

route.find_closest_point(actual_position)
# route.dist2lati_long(actual_position, delta_spacing)