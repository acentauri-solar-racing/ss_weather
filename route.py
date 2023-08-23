import pandas as pd
import numpy as np
import os
import constants
from scipy.spatial import KDTree

class Route():
    
    def __init__(self) -> None:
        self.route_data = self._load_route_csv()
        self.kdtree = KDTree(self.route_data[['latitude', 'longitude']].values)

    def _load_route_csv(self):
        script_directory = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_directory, constants.ROUTE)
        route_data = pd.read_csv(csv_file_path)
        return route_data
    
    def _check_variables(self, variables:dict) -> None:
        validation_rules = {
            'latitude': (float, -90.0, 90.0),
            'longitude': (float, -180.0, 180.0),
            'number_sites': (int, 1, 3000),
            'delta_spacing': (float, 1, 3000000) # in meters
        }

        for variable, value in variables.items():
            if variable in validation_rules:
                value_type, min_value, max_value = validation_rules[variable]

                if value is not None:
                    if not isinstance(value, value_type):
                        raise ValueError(f'{variable} has to be a {value_type}. Received: {value}')

                    if min_value is not None and max_value is not None:
                        if not (min_value <= value <= max_value):
                            raise ValueError(f'{variable} has to be between {min_value} and {max_value}. Received: {value}')
            else:
                raise ValueError(f'Wrong variable. Received: {variable}')
    
    def find_closest_point(self, position:dict):
        self._check_variables(position)

        actual_coords = (position['latitude'], position['longitude'])

        # Query the k-d tree to find the nearest point index
        nearest_point_index = self.kdtree.query([actual_coords], k=1)[1][0]        
        closest_point = self.route_data.iloc[nearest_point_index]
        return closest_point

    def get_final_data(self, current_position:dict, number_sites:int=None, delta_spacing:float=None) -> pd.DataFrame:
        self._check_variables(current_position)

        closest_point = self.find_closest_point(position=current_position)
        start_index = closest_point.name
        start_distance = self.route_data.iloc[start_index]['cumDistance']

        # Cut data and start the cumulative distance from the new position
        cut_data = self.route_data.iloc[start_index:].copy()
        cut_data['cumDistance'] -= start_distance
        # Drop old indexing
        cut_data = cut_data.reset_index(drop=True)
        # Delete surface type
        cut_data = cut_data.drop('surface', axis=1)

        if number_sites is None and delta_spacing is None:
            print(cut_data)
            return cut_data
        
        else:
            add_last_point_is_true: bool = True
            if number_sites is not None:
                delta_spacing = cut_data['cumDistance'].max() / (number_sites - 1) # correction of first entry
                add_last_point_is_true = False

            # Save variables and check
            variables = {
                'number_sites': number_sites,
                'delta_spacing': delta_spacing
            }
            self._check_variables(variables)
        
            # Find value of interpolation points
            number_inter_point = int(cut_data['cumDistance'].max() / delta_spacing)
            # Define the monotonically-increasing equally-spaced vector
            x = np.arange(number_inter_point + 1) * delta_spacing

            # Insert last point
            if add_last_point_is_true:
                x = np.append(x, cut_data['cumDistance'].max())

            # Interpolation points
            xp = cut_data['cumDistance']

            interpolated_data = pd.DataFrame()
            for column in cut_data.columns:

                if column == 'maxSpeed':
                    indices = np.searchsorted(xp, x, side='right') - 1
                    pd_values = pd.DataFrame({column: cut_data[column].iloc[indices]})
                    pd_values = pd_values.reset_index(drop=True)
                    interpolated_data = pd.concat([interpolated_data, pd_values], axis=1)

                elif column == 'cumDistance':
                    interpolated_data[column] = x.tolist()

                else:
                    fp = cut_data[column]
                    interpolated_values = np.interp(x, xp, fp)
                    interpolated_data[column] = interpolated_values.tolist()
            
            print(interpolated_data)
            return interpolated_data