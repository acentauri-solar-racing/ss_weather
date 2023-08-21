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
    
    def check_variables(self, variables) -> None:
        validation_rules = {
            'latitude': (float, -90.0, 90.0),
            'longitude': (float, -180.0, 180.0)
        }

        for variable, value in variables.items():
            if variable in validation_rules:
                value_type, min_value, max_value = validation_rules[variable]

                if not isinstance(value, value_type):
                    raise ValueError(f'{variable} has to be a {value_type}. Received: {value}')

                if min_value is not None and max_value is not None:
                    if not (min_value <= value <= max_value):
                        raise ValueError(f'{variable} has to be between {min_value} and {max_value}. Received: {value}')
            else:
                raise ValueError(f'Wrong variable. Received: {variable}')
    
    def find_closest_point(self, position: dict):
        self.check_variables(position)

        actual_coords = (position['latitude'], position['longitude'])

        # Query the k-d tree to find the nearest point index
        nearest_point_index = self.kdtree.query([actual_coords], k=1)[1][0]        
        closest_point = self.route_data.iloc[nearest_point_index]
        return closest_point

    def get_final_data(self, current_position: dict, delta_spacing: float = None):
        self.check_variables(current_position)

        closest_point = self.find_closest_point(position=current_position)

        start_index = closest_point.name
        start_distance = self.route_data.iloc[start_index]['CumDistance']

        # Cut data and start the cumulative distance from the new position
        cut_data = self.route_data.iloc[start_index:].copy()
        cut_data['CumDistance'] -= start_distance
        # Drop old indexing
        cut_data = cut_data.reset_index(drop=True)
        # Delete Surface type
        cut_data = cut_data.drop('Surface', axis=1)

        if delta_spacing is None:
            return cut_data
        
        else:
            if not isinstance(delta_spacing, int) or (self.min_delta_spacing > delta_spacing > self.max_delta_spacing):
                raise ValueError(f'{delta_spacing} has to be an integer between {self.min_delta_spacing} and {self.max_delta_spacing}. Received: {delta_spacing}')

            # Find value of interpolation points
            number_inter_point = int(cut_data['CumDistance'].max() / delta_spacing)
            # Define the monotonically-increasing equally-spaced vector
            x = np.arange(number_inter_point + 2) * delta_spacing
            # Insert last point
            x[-1] = cut_data['CumDistance'].max()
            # Interpolation points
            xp = cut_data['CumDistance']

            interpolated_data = pd.DataFrame()
            for column in cut_data.columns:

                if column == 'Maxspeed':
                    indices = np.searchsorted(xp, x, side='right') - 1
                    pd_values = pd.DataFrame({column: cut_data[column].iloc[indices]})
                    pd_values = pd_values.reset_index(drop=True)
                    interpolated_data = pd.concat([interpolated_data, pd_values], axis=1)

                elif column == 'CumDistance':
                    interpolated_data[column] = x.tolist()

                else:
                    fp = cut_data[column]
                    interpolated_values = np.interp(x, xp, fp)
                    interpolated_data[column] = interpolated_values.tolist()

            return interpolated_data