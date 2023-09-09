import pandas as pd
import numpy as np
import constants
from scipy.spatial import KDTree

class ApiRoute():
    """
    TODO
    """
    
    def __init__(self, route_data:pd.DataFrame) -> None:
        # Save complete route data
        self.route_data = route_data
        self.max_distance = self.route_data['cumDistance'].max()

        # Create k-d tree for searching
        self.kdtree = KDTree(self.route_data[['latitude', 'longitude']].values)
    
    def _check_variables(self, variables:dict) -> None:
        """
        TODO
        """
        validation_rules = {
            'latitude': (float, -90.0, 90.0),
            'longitude': (float, -180.0, 180.0),
            'number_sites': (int, 2, constants.MAX_SITES_NUMBER),
            'delta_spacing': (float, 1, self.max_distance) # in meters
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
    
    def find_closest_point(self, position:dict, print_is_requested:bool=True) -> pd.Series:
        """
        TODO
        """
        self._check_variables(position)

        actual_coords = (position['latitude'], position['longitude'])

        # Query the k-d tree to find the nearest point index
        nearest_point_index = self.kdtree.query([actual_coords], k=1)[1][0]

        if print_is_requested:
            print('Nearest point index:', nearest_point_index)

        closest_point = self.route_data.iloc[nearest_point_index]
        return closest_point

    def cut_route_data(self, current_position:dict=None, final_position:dict=None, number_sites:int=None, delta_spacing:float=None, print_is_requested:bool=True) -> pd.DataFrame:
        """
        TODO
        """
        cut_data = self.route_data.copy()

        # Delete columns that are not needed
        cut_data = cut_data.drop('inclination', axis=1)
        cut_data = cut_data.drop('inclinationSmooth', axis=1)
        cut_data = cut_data.drop('altitude', axis=1)
        cut_data = cut_data.drop('distance', axis=1)

        # Add cumulative distance column
        cut_data = pd.concat([cut_data, pd.DataFrame({'cumDistanceCut': cut_data['cumDistance']})], axis=1)

        # If all inputs are None
        if current_position is None and final_position is None and number_sites is None and delta_spacing is None:
            return cut_data
        
        # Initialize start and end index
        start_index = 0
        # end_index = len(cut_data)
        
        # If current position is given
        if current_position is not None:
            closest_point = self.find_closest_point(position=current_position, print_is_requested=print_is_requested)
            start_index = closest_point.name

            # Subtract cumulative distance
            start_distance = cut_data.iloc[start_index]['cumDistance']
            cut_data['cumDistanceCut'] -= start_distance

            # Cut data and reset indexing
            cut_data = cut_data.iloc[start_index:].copy()
            cut_data = cut_data.reset_index(drop=True)

        # If final position is given
        if final_position is not None:
            if number_sites is not None and delta_spacing is not None:
                raise ValueError('The final position cannot be given with number_sites and delta_spacing')
            
            closest_point = self.find_closest_point(position=final_position, print_is_requested=print_is_requested)
            end_index = closest_point.name

            if end_index < start_index:
                raise ValueError('The final position is before the start position')

            # Cut data
            cut_index = end_index - start_index + 1 # -start_index,+1 to include previous cut and final position
            cut_data = cut_data.iloc[:cut_index].copy()

        # Variable to add last point for interpolation
        add_last_point_is_true: bool = True

        # None of the variables are given
        if number_sites is None and delta_spacing is None:
            return cut_data
        
        # Both variables are given
        elif number_sites is not None and delta_spacing is not None: # Case with final position already considered
            total_distance = number_sites * delta_spacing
            end_distance = cut_data.iloc[-1]['cumDistanceCut']

            if total_distance > end_distance:
                raise ValueError('The total distance is greater than the end distance of the route')
            
            # Cut data
            cut_data = cut_data.loc[cut_data['cumDistanceCut'] <= total_distance].copy()
            add_last_point_is_true = False
        
        # Only number_sites is given
        elif number_sites is not None and delta_spacing is None:
            # Calculate delta spacing
            delta_spacing = cut_data['cumDistanceCut'].max() / (number_sites - 1) # correction of first entry
            add_last_point_is_true = False

        # Only delta_spacing is given
        elif number_sites is None and delta_spacing is not None:
            # Nothing to do
            pass
        
        # Save variables and check
        variables = {
            'number_sites': number_sites,
            'delta_spacing': delta_spacing
        }
        self._check_variables(variables)
    
        # Find values to be interpolated
        number_inter_point = int(cut_data['cumDistanceCut'].max() / delta_spacing)
        # Define the monotonically-increasing equally-spaced vector
        x = np.arange(number_inter_point + 1) * delta_spacing

        # Insert last point
        if add_last_point_is_true:
            x = np.append(x, cut_data['cumDistanceCut'].max())

        # Interpolation points
        xp = cut_data['cumDistanceCut']

        interpolated_data = pd.DataFrame()
        for column in cut_data.columns:
            if column == 'maxSpeed':
                # Find previous index and corresponding value
                indices = np.searchsorted(xp, x, side='right') - 1
                pd_values = pd.DataFrame({column: cut_data[column].iloc[indices]})
                pd_values = pd_values.reset_index(drop=True)

                # Concatenate interpolated data
                interpolated_data = pd.concat([interpolated_data, pd_values], axis=1)

            elif column == 'cumDistanceCut':
                # Convert to list and add to interpolated data
                interpolated_data[column] = x.tolist()

            else:
                # Perform interpolation
                fp = cut_data[column]
                interpolated_values = np.interp(x, xp, fp)
                interpolated_data[column] = interpolated_values.tolist()
        
        if print_is_requested:
            print(interpolated_data)

        return interpolated_data