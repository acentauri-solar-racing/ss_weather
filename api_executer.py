import pandas as pd
from typing import Tuple
from api_requester import ApiRequester

class ApiExecuter():
    """ Class for calling multiple times requester functions.

    Attributes:
        requester (ApiRequester): The requester object. """

    def __init__(self, requester:ApiRequester, print_is_requested:bool=False) -> None:
        self.requester = requester
        self.print_is_requested = print_is_requested

    @property
    def get_all_site_id(self) -> list:
        """ Returns a list with all sites id. """

        site_info_df = self.requester.get_site_info()
        return site_info_df.index.tolist()

    def _check_sites_id(self, sites_id_to_check:list) -> None:
        """ Check that all sites id are present in the site info DataFrame.
        
            Inputs:
                sites_id (list): The list of sites id to check. """

        sets_are_equal = set(self.get_all_site_id) == set(sites_id_to_check)

        if not sets_are_equal:
            raise ValueError('Some sites id are not present in the site info.')

    def add_sites(self, to_add_df:pd.DataFrame, print_is_requested:bool=False) -> None:
        """ Add multiple sites by calling the requester given the route dataframe. The name is automatically created as incremental number.
        
            Inputs:
                to_add_df (pd.DataFrame): Dataframe with latitude and longitude columns.
                print_is_requested (bool): Whether to print the requested sites. """
        
        # Check that the dataframe has the right columns
        if 'latitude' not in to_add_df.columns or 'longitude' not in to_add_df.columns:
            raise ValueError('The dataframe has to have latitude and longitude columns.')
        
        count = 0
        for _, row in to_add_df.iterrows():
            name = str(count)
            latitude = row['latitude']
            longitude = row['longitude']

            self.requester.get_site_add(name=name, latitude=latitude, longitude=longitude, print_is_requested=print_is_requested)
            count += 1

        if self.print_is_requested or print_is_requested:
            print(f"Requested sites have been added: \n {self.requester.forecast_sites}")

    def edit_sites(self, to_edit_df:pd.DataFrame, print_is_requested:bool=False) -> None:
        """ Edit multiple sites by calling the requester given the route dataframe.
            
            Inputs:
                to_edit_df (pd.DataFrame): The sites dataframe with site_id as index and name, latitude, and longitude as columns.
                    for unchaged name: * = None, * = '', or column not given
                    for unchaged latitude or longitude: * = None, * = NaN, or columns not given
                    both longitude and latitude have to be provided to change the position
                print_is_requested (bool): Whether to print the requested sites. """

        self._check_sites_id(to_edit_df.index.tolist())

        for site_id in to_edit_df.index:
            change_name = True
            change_position = True

            # Check if the name column exists
            if 'name' not in to_edit_df.columns:
                change_name = False
            
            # Check if the position columns exist
            if 'latitude' not in to_edit_df.columns or 'longitude' not in to_edit_df.columns:
                change_position = False

            # Extract the value to change
            if change_name and change_position:
                name = to_edit_df.loc[site_id, 'name']
                latitude = to_edit_df.loc[site_id, 'latitude']
                longitude = to_edit_df.loc[site_id, 'longitude']
                position = {'longitude': longitude, 'latitude': latitude}
                self.requester.get_site_edit(site_id, print_is_requested=print_is_requested, name=name, position=position)
            
            elif change_name:
                name = to_edit_df.loc[site_id, 'name']
                self.requester.get_site_edit(site_id, print_is_requested=print_is_requested, name=name)
            
            elif change_position:
                latitude = to_edit_df.loc[site_id, 'latitude']
                longitude = to_edit_df.loc[site_id, 'longitude']
                position = {'longitude': longitude, 'latitude': latitude}
                self.requester.get_site_edit(site_id, print_is_requested=print_is_requested, position=position)
            else:
                print("Nothing to change for this site.")
                return

        if self.print_is_requested or print_is_requested:
            print(f"Requested sites have been edited: \n {self.requester.forecast_sites}")

    def delete_sites(self, to_delete_df:pd.DataFrame, print_is_requested:bool=False) -> None:
        """ Delete multiple sites by calling the requester given the sites dataframe.
            
            Inputs:
                to_delete_df (pd.DataFrame): Dataframe with site id index.
                print_is_requested (bool): Whether to print the requested sites. """

        self._check_sites_id(to_delete_df.index.tolist())

        for site_id in to_delete_df.index:
            self.requester.get_site_delete(site_id, print_is_requested=print_is_requested)

        if self.print_is_requested or print_is_requested:
            print(f"Requested sites have been deleted: \n {self.requester.forecast_sites}")

    def delete_all_sites(self, print_is_requested:bool=False) -> None:
        """ Delete all sites by calling the requester.
        
            Inputs:
                print_is_requested (bool): Whether to print the requested sites. """
        
        sites_id_list = self.get_all_site_id
        for site_id in sites_id_list:
            self.requester.get_site_delete(site_id, print_is_requested=print_is_requested)
        
        if self.print_is_requested or print_is_requested:
            print(f"All sites have been deleted: \n {self.requester.forecast_sites}")

    def get_new_solar_forecast(self) -> Tuple[pd.DataFrame, bool]:
        """ """
        new_forecast_df = self.requester.get_solar_forecast()

        if new_forecast_df.iloc[:2].equals(self.requester.previous_SF_df.iloc[:2]):
            new_forecast_arrived = False
            new_forecast_df = None
            print("No new SF forecast")
        else:
            new_forecast_arrived = True
            print("New SF forecast arrived")
        
        return new_forecast_df, new_forecast_arrived
    
    def get_new_solar_forecast_cloudmove(self) -> Tuple[pd.DataFrame, bool]:
        """ """
        new_forecast_df = self.requester.get_solar_forecast_cloudmove()

        if new_forecast_df.iloc[:2].equals(self.requester.previous_CM_df.iloc[:2]):
            new_forecast_arrived = False
            new_forecast_df = None
            print("No new CM forecast")
        else:
            new_forecast_arrived = True
            print("New CM forecast arrived")
        
        return new_forecast_df, new_forecast_arrived