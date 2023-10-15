import pandas as pd
import os
import constants
import tkinter as tk
from typing import Tuple
from tkinter import filedialog
from scipy.spatial import KDTree

class Route():
    """ Import the route data from the csv file and generate a Pandas DataFrame. 
    
        Args:
            choose_specific_route (bool): If True, a file dialog will open to allow the user to choose a specific route file. 
                If False, the route file specified in constants.py will be used. Defaults to False. """
    
    def __init__(self, choose_specific_route:bool=False) -> None:
        # Upload route data
        if choose_specific_route:
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            root.lift()  # Bring the window to the front
            root.attributes('-topmost', True)  # Keep the window on top of all others

            chosen_file = filedialog.askopenfilename(title='Select the csv route file', filetypes=[("CSV files", "*.csv")])

            if chosen_file:
                self.route_df = pd.read_csv(chosen_file)
                print(f"Data read from {chosen_file}.")
            else:
                print("No directory chosen. Data not read.")

            
            # Upload control stops
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            root.lift()  # Bring the window to the front
            root.attributes('-topmost', True)  # Keep the window on top of all others

            chosen_file = filedialog.askopenfilename(title='Select the csv file with control stops', filetypes=[("CSV files", "*.csv")])

            if chosen_file:
                self.control_stops_df = pd.read_csv(chosen_file)
                print(f"Data read from {chosen_file}.")
            else:
                print("No directory chosen. Data not read.")
        
        else:
            # Upload route data
            script_directory = os.path.dirname(os.path.abspath(__file__))
            csv_file_path = os.path.join(script_directory, constants.ROUTE)
            self.route_df = pd.read_csv(csv_file_path)


            # Upload control stops
            script_directory = os.path.dirname(os.path.abspath(__file__))
            csv_file_path = os.path.join(script_directory, constants.CONTROL_STOPS)
            self.control_stops_df = pd.read_csv(csv_file_path)


        # Create k-d tree for searching
        self.kdtree_geo = KDTree(self.route_df[['latitude', 'longitude']].values)

    @property
    def get_route_data(self) -> pd.DataFrame:
        """ Return the route data as a Pandas DataFrame. """
        return self.route_df
    
    @property
    def get_control_stops_data(self) -> pd.DataFrame:
        """ Return the control stop data as a Pandas DataFrame. """
        return self.control_stops_df
    
    def _check_variables(self, variables:dict) -> None:
        """ Check if the variables are of the correct type and between the ranges. 
        
            Inputs:
                variables (dict): The variables to be checked. """

        validation_rules = {
            'latitude': (float, constants.GEO['latitude']['min'], constants.GEO['latitude']['max']),
            'longitude': (float, constants.GEO['longitude']['min'], constants.GEO['longitude']['max'])
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
            
    
    def find_closest_row_cumDistance(self, cum_distance:float, print_is_requested:bool=False) -> Tuple[pd.Series, bool]:
        """ """
        # Check that cumDistance is between the range
        if not (self.route_df['cumDistance'].min() <= cum_distance <= self.route_df['cumDistance'].max()):
            raise ValueError(f'Cumulative distance has to be between {self.route_df["cumDistance"].min()} and {self.route_df["cumDistance"].max()}. Received: {cum_distance}')
        
        nearest_point_index = self.route_df['cumDistance'].searchsorted(cum_distance, side='left')
            
        closest_row = self.route_df.iloc[nearest_point_index]

        if print_is_requested:
            print('Nearest index in csv file:', nearest_point_index + 2)
            print('Nearest index in dataframe:', nearest_point_index)

        return closest_row, nearest_point_index
    
    def find_closest_row(self, position:dict, print_is_requested:bool=False) -> Tuple[pd.Series, int]:
        """ Find the closest row in the route to the given position.

            Inputs:
                position (dict): The position with latitude and longitude keys.
                print_is_requested (bool): Whether to print the nearest point index. """
        
        self._check_variables(position)

        actual_coords = (position['latitude'], position['longitude'])

        # Query the k-d tree to find the nearest point index
        nearest_point_index = self.kdtree_geo.query([actual_coords], k=1)[1][0]
        closest_row = self.route_df.iloc[nearest_point_index]

        if print_is_requested:
            print('Nearest index in csv file:', nearest_point_index + 2)
            print('Nearest index in dataframe:', nearest_point_index)

        return closest_row, nearest_point_index
    
    def find_closest_rows(self, position_df:pd.DataFrame, print_is_requested:bool=False) -> pd.DataFrame:
        """ Find the closest rows in the route to the given positions.

            Inputs:
                positions (pd.DataFrame): The positions with latitude and longitude columns.
                print_is_requested (bool): Whether to print the nearest point index. """
        
        closest_rows_and_indices = position_df.apply(lambda row: self.find_closest_row({'latitude': row['latitude'], 'longitude': row['longitude']}, print_is_requested), axis=1)
        closest_rows_df = pd.DataFrame(closest_rows_and_indices.tolist(), columns=['closest_row', 'index'])
        return closest_rows_df
    
    def insert_to_control_stops(self, choose_specific_route:bool=False) -> None:
        """ Insert the cumDistance column to the control stops data. """

        closest_rows_df = self.find_closest_rows(self.control_stops_df[['latitude', 'longitude']])
        print(closest_rows_df['index'].values)
        self.control_stops_df['cumDistance'] = closest_rows_df['closest_row'].apply(lambda x: x['cumDistance']).values
        self.control_stops_df['dfIndex'] = closest_rows_df['index'].values
        self.control_stops_df['csvIndex'] = closest_rows_df['index'].values + 2
            
        if choose_specific_route:
            # Save the control stops data to a specific file
            root = tk.Tk()
            root.withdraw()
            root.lift()
            root.attributes('-topmost', True)

            chosen_file = filedialog.asksaveasfilename(title='Save the control stops data to a csv file', filetypes=[("CSV files", "*.csv")])

            if chosen_file:
                self.control_stops_df.to_csv(chosen_file, index=False)
                print(f"Control stops data saved to {chosen_file}.")

        else:
            script_directory = os.path.dirname(os.path.abspath(__file__))
            csv_file_path = os.path.join(script_directory, constants.CONTROL_STOPS)
            self.control_stops_df.to_csv(csv_file_path, index=False)
        
            print(f"Control stops data saved to {csv_file_path}.")