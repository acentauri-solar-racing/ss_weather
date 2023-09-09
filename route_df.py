import pandas as pd
import os
import constants

class RouteDF():
    """
    Import the route data from the csv file and generate a Pandas DataFrame.
    """
    
    def __init__(self) -> None:
        script_directory = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(script_directory, constants.ROUTE) # CHANGE THIS TO WINDOW AS GUI

        self.route_data = pd.read_csv(csv_file_path)

    def get_route_data(self) -> pd.DataFrame:
        return self.route_data