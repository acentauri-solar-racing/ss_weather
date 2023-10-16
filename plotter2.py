import pandas as pd
from route import Route

class Plotter2():
    """ """
    def __init__(self, route:Route) -> None:
        self.route = route
        self.route_data = self.route.get_route_data
        self.control_stops = self.route.get_control_stops_data

        min_lng = self.route_data['longitude'].min()
        min_lat = self.route_data['latitude'].min()
        max_lng = self.route_data['longitude'].max()
        max_lat = self.route_data['latitude'].max()

        # Create a base map centered around the midle of the route
        middle_lat = (max_lat + min_lat) / 2
        middle_lng = (max_lng + min_lng) / 2