import pandas as pd
from api_requester import ApiRequester

class ApiExecuter():
    """ Class for calling multiple times requester functions.

    Attributes:
        requester (ApiRequester): The requester object. """

    def __init__(self, requester:ApiRequester) -> None:
        self.requester = requester

    def add_sites(self, route_df:pd.DataFrame, print_is_requested:bool=True) -> None:
        """ Add multiple sites by calling the requester given the route dataframe. 
        
            Inputs:
                route_df (pd.DataFrame): The route dataframe with latitude and longitude columns.
                print_is_requested (bool): Whether to print the requested sites. """

        if not isinstance(route_df, pd.DataFrame):
            raise ValueError('dataframe must be a Pandas DataFrame.')
        # TODO CHECK DATAFRAME STRUCTURE
        
        count = 0
        for _, row in route_df.iterrows():
            name = str(count)
            latitude = row['latitude']
            longitude = row['longitude']

            self.requester.get_site_add(name=name, latitude=latitude, longitude=longitude, print_is_requested=print_is_requested)
            count += 1

        if print_is_requested:
            print(f"Requested sites have been added: \n {self.requester.forecast_sites}")

    def delete_sites(self, route_df:pd.DataFrame, print_is_requested:bool=True) -> None:
        """ Delete multiple sites by calling the requester given the sites dataframe.
            
            Inputs:
                route_df (pd.DataFrame): The route dataframe with latitude and longitude columns.
                print_is_requested (bool): Whether to print the requested sites. """
        
        if not isinstance(route_df, pd.DataFrame):
            raise ValueError('dataframe must be a Pandas DataFrame.')
        # TODO CHECK DATAFRAME STRUCTURE

        for site_id in route_df.index:
            self.requester.get_site_delete(site_id, print_is_requested=print_is_requested)

            self.requester.get_site_delete(site_id, print_is_requested=print_is_requested)

        if print_is_requested:
            print(f"Requested sites have been deleted: \n {self.requester.forecast_sites}")

    def delete_all_sites(self, print_is_requested:bool=True) -> None:
        """ Delete all sites by calling the requester.
        
            Inputs:
                print_is_requested (bool): Whether to print the requested sites. """
        
        for site_id in self.requester.forecast_sites.index:
            self.requester.get_site_delete(site_id, print_is_requested=print_is_requested)
        
        if print_is_requested:
            print(f"All sites have been deleted: \n {self.requester.forecast_sites}")