import pandas as pd
from api_requester import ApiRequester

class ApiExecuter():
    """ Class for calling multiple times requester functions.

    Attributes:
        requester (ApiRequester): The requester object. """

    def __init__(self, requester:ApiRequester) -> None:
        self.requester = requester

    def _check_sites_id(self, sites_id_to_check:list) -> None:
        """ Check that all sites id are present in the site info dataframe.
        
            Inputs:
                sites_id (list): The list of sites id to check."""

        sites_id_list = self.get_all_site_id(print_is_requested=False)
        are_equal = set(sites_id_list) == set(sites_id_to_check)

        if not are_equal:
            raise ValueError('Some sites id are not present in the site info.')

    def add_sites(self, to_add_df:pd.DataFrame, print_is_requested:bool=True) -> None:
        """ Add multiple sites by calling the requester given the route dataframe. The name is automatically created as incremental number.
        
            Inputs:
                to_add_df (pd.DataFrame): Dataframe with latitude and longitude columns.
                print_is_requested (bool): Whether to print the requested sites."""

        if not isinstance(to_add_df, pd.DataFrame):
            raise ValueError('dataframe must be a Pandas DataFrame.')
        
        count = 0
        for _, row in to_add_df.iterrows():
            name = str(count)
            latitude = row['latitude']
            longitude = row['longitude']

            self.requester.get_site_add(name=name, latitude=latitude, longitude=longitude, print_is_requested=print_is_requested)
            count += 1

        if print_is_requested:
            print(f"Requested sites have been added: \n {self.requester.forecast_sites}")

    def edit_sites(self, edit_df:pd.DataFrame, print_is_requested:bool=False) -> None:
        """ Edit multiple sites by calling the requester given the route dataframe.
            
            Inputs:
                edit_df (pd.DataFrame): The sites dataframe with site_id as index and name, latitude, and longitude as columns.
                    for unchaged name: * = None, * = '', column not given
                    for unchaged latitude or longitude: * = None, * = NaN, or columns not given
                    both longitude and latitude have to be provided to change the position
                print_is_requested (bool): Whether to print the requested sites."""
        
        if not isinstance(edit_df, pd.DataFrame):
            raise ValueError('dataframe must be a Pandas DataFrame.')

        # Check that all sites id are correct
        self._check_sites_id(edit_df.index.tolist())

        for site_id in edit_df.index:
            change_name = True
            change_position = True

            # Check if the name column exists
            if 'name' not in edit_df.columns:
                change_name = False
            
            # Check if the position columns exist
            if 'latitude' not in edit_df.columns or 'longitude' not in edit_df.columns:
                change_position = False

            # Extract the value to change
            if change_name and change_position:
                name = edit_df.loc[site_id, 'name']
                latitude = edit_df.loc[site_id, 'latitude']
                longitude = edit_df.loc[site_id, 'longitude']
                position = {'longitude': longitude, 'latitude': latitude}
                self.requester.get_site_edit(site_id, print_is_requested=print_is_requested, name=name, position=position)
            
            elif change_name:
                name = edit_df.loc[site_id, 'name']
                self.requester.get_site_edit(site_id, print_is_requested=print_is_requested, name=name)
            
            elif change_position:
                latitude = edit_df.loc[site_id, 'latitude']
                longitude = edit_df.loc[site_id, 'longitude']
                position = {'longitude': longitude, 'latitude': latitude}
                self.requester.get_site_edit(site_id, print_is_requested=print_is_requested, position=position)
            else:
                print("Nothing to change for this site.")

        if print_is_requested:
            print(f"Requested sites have been edited: \n {self.requester.forecast_sites}")

    def delete_sites(self, delete_df:pd.DataFrame, print_is_requested:bool=True) -> None:
        """ Delete multiple sites by calling the requester given the sites dataframe.
            
            Inputs:
                delete_df (pd.DataFrame): Dataframe with site id index.
                print_is_requested (bool): Whether to print the requested sites."""
        
        if not isinstance(delete_df, pd.DataFrame):
            raise ValueError('dataframe must be a Pandas DataFrame.')
        
        # Check site id
        self._check_sites_id(delete_df.index.tolist())

        for site_id in delete_df.index:
            self.requester.get_site_delete(site_id, print_is_requested=print_is_requested)

        if print_is_requested:
            print(f"Requested sites have been deleted: \n {self.requester.forecast_sites}")

    def delete_all_sites(self, print_is_requested:bool=True) -> None:
        """ Delete all sites by calling the requester.
        
            Inputs:
                print_is_requested (bool): Whether to print the requested sites."""
        
        for site_id in self.get_all_site_id(print_is_requested=False):
            self.requester.get_site_delete(site_id, print_is_requested=print_is_requested)
        
        if print_is_requested:
            print(f"All sites have been deleted: \n {self.requester.forecast_sites}")

    def get_all_site_id(self, print_is_requested:bool=False) -> list:
        """ Returns a list with all sites id.
        
            Inputs:
                print_is_requested (bool): Whether to print the requested sites."""

        site_info_df = self.requester.get_site_info(print_is_requested=print_is_requested)

        return site_info_df.index.tolist()