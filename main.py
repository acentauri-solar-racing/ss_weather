import pandas as pd
import numpy as np

from route import Route
from api_requester import ApiRequester
from api_parser import ApiParser
from api_executer import ApiExecuter
# from api_data import ApiData
from FUNCTIONS import get_current_location

current_position = {'longitude': 130.868566,
                    'latitude': -12.432466}
delta_spacing = 100000.0 # in meters
number_sites = 3

route = Route()
# route.get_final_data(current_position)
# route.get_final_data(current_position, delta_spacing=delta_spacing)
dataframe = route.get_route_data(current_position, number_sites=number_sites)

api_parser = ApiParser()
api_requester = ApiRequester(parser=api_parser)
api_executer = ApiExecuter(requester=api_requester)

api_executer.add_sites(dataframe, print_is_requested=False)