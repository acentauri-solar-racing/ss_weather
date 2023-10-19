import os
import constants
import pandas as pd
import tkinter as tk
from typing import Tuple
from tkinter import filedialog
from scipy.spatial import KDTree

class Route():
    """ Import the route data from the csv file and generate a Pandas DataFrame. 
    
        Args:
            choose_specific_route (bool): If True, a file dialog will open to allow the user to choose a specific route file. 
                If False, the route file specified in constants.py will be used. Defaults to False. """
    
    def __init__(self, choose_specific:bool=False) -> None:
        # Upload route data
        if choose_specific:
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

            # Upload camping
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            root.lift()  # Bring the window to the front
            root.attributes('-topmost', True)  # Keep the window on top of all others

            chosen_file = filedialog.askopenfilename(title='Select the csv file with camping data', filetypes=[("CSV files", "*.csv")])

            if chosen_file:
                self.camping_df = pd.read_csv(chosen_file)
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

            # Upload camping data
            script_directory = os.path.dirname(os.path.abspath(__file__))
            csv_file_path = os.path.join(script_directory, constants.CAMPING)
            self.camping_df = pd.read_csv(csv_file_path)

        # Create k-d tree for searching
        self.kdtree_route = KDTree(self.route_df[['latitude', 'longitude']].values)
        # self.kdtree_cs = KDTree(self.control_stops_df[['latitude', 'longitude']].values)

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
            'longitude': (float, constants.GEO['longitude']['min'], constants.GEO['longitude']['max']),
            'cumDistance': ((float, int), self.route_df['cumDistance'].min(), self.route_df['cumDistance'].max()),
            'cumDistance_km': ((float, int), self.route_df['cumDistance'].min() / 1000, self.route_df['cumDistance'].max() / 1000)
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
        nearest_point_index = self.kdtree_route.query([actual_coords], k=1)[1][0]
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
    
    def insert_to_control_stops(self, choose_specific:bool=False) -> None:
        """ Insert the cumDistance column to the control stops data. """

        closest_rows_df = self.find_closest_rows(self.control_stops_df[['latitude', 'longitude']])

        self.control_stops_df['cumDistance'] = closest_rows_df['closest_row'].apply(lambda x: x['cumDistance']).values
        self.control_stops_df['dfIndex'] = closest_rows_df['index'].values
        self.control_stops_df['csvIndex'] = closest_rows_df['index'].values + 2
            
        if choose_specific:
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

    def find_next_cs_cumDistance(self, current_cum_distance:float, print_is_requested:bool=False) -> Tuple[pd.Series, bool]:
        """ """
        # Check that cumDistance is between the range
        if not (self.route_df['cumDistance'].min() <= current_cum_distance <= self.route_df['cumDistance'].max()):
            raise ValueError(f'Cumulative distance has to be between {self.route_df["cumDistance"].min()} and {self.route_df["cumDistance"].max()}. Received: {current_cum_distance}')
        
        nearest_point_index = self.control_stops_df['cumDistance'].searchsorted(current_cum_distance, side='left')
        
        closest_row = self.control_stops_df.iloc[nearest_point_index]

        if print_is_requested:
            print('Nearest index in csv file:', nearest_point_index + 2)
            print('Nearest index in dataframe:', nearest_point_index)

        return closest_row, nearest_point_index
    
    def find_next_cs(self, position:dict, print_is_requested:bool=False) -> Tuple[pd.Series, int]:
        """ """
        
        self._check_variables(position)

        row, _ = self.find_closest_row(position, print_is_requested=print_is_requested)

        # Find the first cumDistance > row['cumDistance'] in control stop not the closest one
        next_rows = self.control_stops_df[self.control_stops_df['cumDistance'] > row['cumDistance']]
        
        if next_rows.empty:
            print("There's no next control stop. The closest control stop might be the last one on the route.")
            return None, None
        
        next_index = next_rows.index[0]
        next_row = self.control_stops_df.iloc[next_index]

        if print_is_requested:
            print('Nearest index in csv file:', next_index + 2)
            print('Nearest index in dataframe:', next_index)

        return next_row, next_index
    
    def insert_to_camping(self, choose_specific:bool=False) -> None:
        """ Insert the cumDistance column to the control stops data. """

        closest_rows_df = self.find_closest_rows(self.camping_df[['latitude', 'longitude']])

        self.camping_df['cumDistance'] = closest_rows_df['closest_row'].apply(lambda x: x['cumDistance']).values
        self.camping_df['dfIndex'] = closest_rows_df['index'].values
        self.camping_df['csvIndex'] = closest_rows_df['index'].values + 2
            
        if choose_specific:
            # Save the camping data to a specific file
            root = tk.Tk()
            root.withdraw()
            root.lift()
            root.attributes('-topmost', True)

            chosen_file = filedialog.asksaveasfilename(title='Save the camping data to a csv file', filetypes=[("CSV files", "*.csv")])

            if chosen_file:
                self.camping_df.to_csv(chosen_file, index=False)
                print(f"Camping data saved to {chosen_file}.")

        else:
            script_directory = os.path.dirname(os.path.abspath(__file__))
            csv_file_path = os.path.join(script_directory, constants.CAMPING)
            self.camping_df.to_csv(csv_file_path, index=False)
        
            print(f"Camping data saved to {csv_file_path}.")