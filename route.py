import pandas as pd
import numpy as np
import os
import constants
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
        cut_data = self.route_data.iloc[start_index:]
        cut_data['CumDistance'] -= start_distance
        # Drop old indexing
        cut_data = cut_data.reset_index(drop=True)
        # Delete Surface type
        cut_data = cut_data.drop('Surface', axis=1)

        if delta_spacing is None:
            print(cut_data)
            return cut_data
        else:
            if not isinstance(delta_spacing, int) or (self.min_delta_spacing > delta_spacing > self.max_delta_spacing):
                raise ValueError(f'{delta_spacing} has to be an integer between {self.min_delta_spacing} and {self.max_delta_spacing}. Received: {delta_spacing}')

            # Create a copy of the first row for interpolated data
            interpolated_data = cut_data.iloc[[0]]
            # Find value of interpolation points
            number_inter_point = int(cut_data['CumDistance'].max() / delta_spacing)
            # Define the ascending equally-spaced vector
            x = np.arange(number_inter_point + 2) * delta_spacing
            x[-1] = cut_data['CumDistance'].max()
            # Interpolation points
            xp = cut_data['CumDistance']

            # Interpolate selected columns
            for column in cut_data.columns:
                print(interpolated_data)

                if column == 'Maxspeed':
                    # Find the indices of x in xp (closest smaller indices)
                    indices = np.searchsorted(xp, x, side='right') - 1
                    interpolated_data[column] = cut_data[column].iloc[indices]

                elif column == 'CumDistance':
                    interpolated_data[column] = pd.Series(x)

                else:
                    fp = cut_data[column]
                    interpolated_values = np.interp(x, xp, fp)
                    # interpolated_data.loc[:, column] = interpolated_values
                    # interpolated_data[column] = interpolated_values
                    interpolated_data[column] = pd.Series(interpolated_values)
            
            return interpolated_data
        
route = Route()
actual_position = {'longitude': 130,
                   'latitude': -12.4}

delta_spacing = 1000000 # in meters
# route.get_final_data(actual_position)
route.get_final_data(actual_position, delta_spacing)

# TODO check all NaN