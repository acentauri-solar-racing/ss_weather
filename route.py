import pandas as pd
import numpy as np
import os
import constants
from geopy.distance import geodesic
from scipy.spatial import KDTree

class Route():
    
    def __init__(self) -> None:
        self.route_data = self.load_route_csv()
        self.kdtree = KDTree(self.route_data[['Latitude', 'Longitude']].values)

        self.min_delta_spacing = 10 # in meters
        self.max_delta_spacing = 500000 # in meters

    def load_route_csv(self):
        script_directory = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_directory, constants.ROUTE)
        route_data = pd.read_csv(csv_file_path)
        return route_data
    
    def find_closest_point(self, position):
        actual_coords = (position['latitude'], position['longitude'])

        # Query the k-d tree to find the nearest point index
        nearest_point_index = self.kdtree.query([actual_coords], k=1)[1][0]        
        closest_point = self.route_data.iloc[nearest_point_index]
        return closest_point

    def get_final_data(self, actual_position: dict, delta_spacing: float = None):
        closest_point = self.find_closest_point(position=actual_position)
        start_index = closest_point.name
        start_distance = self.route_data.iloc[start_index]['CumDistance']

        # Cut data and start the cumulative distance from the new position
        cut_data = self.route_data.iloc[start_index:].copy()
        cut_data['CumDistance'] -= start_distance

        if delta_spacing is None:
            return cut_data
        else:
            if not isinstance(delta_spacing, int) or (self.min_delta_spacing > delta_spacing > self.max_delta_spacing):
                raise ValueError(f'{delta_spacing} has to be an integer between {self.min_delta_spacing} and {self.max_delta_spacing}. Received: {delta_spacing}')

            # Create a copy of the first row for interpolated data
            interpolated_data = cut_data.iloc[[0]].copy()

            interp_number = int(cut_data['CumDistance'].max() / delta_spacing)
            x = np.arange(interp_number + 2) * delta_spacing
            x[-1] = cut_data['CumDistance'].max()

            xp = cut_data['CumDistance']

            # Interpolate selected columns (excluding 'CumDistance')
            for column in cut_data.columns:
                if column != 'CumDistance':
                    fp = cut_data[column]
                    interpolated_data[column] = np.interp(x, xp, fp)

            return interpolated_data