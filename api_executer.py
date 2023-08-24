import time
import pandas as pd
from api_requester import ApiRequester
from api_data_controller import ApiData

class ApiExecuter():
    """
    TODO
    """

    def __init__(self) -> None:
        pass

    def add_sites(self, dataframe:pd.DataFrame, print_is_requested:bool=True) -> None:
        """
        TODO
        """
        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError('dataframe must be a Pandas DataFrame.')

        for index, row in dataframe.iterrows():
            name = str(index)
            latitude = row['latitude']
            longitude = row['longitude']
            # TODO CHECK DATAFRAME STRUCTURE

            ApiRequester.get_site_add(name=name, latitude=latitude, longitude=longitude, print_is_requested=print_is_requested)

        if print_is_requested:
            print(f"Requested sites have been added: \n {ApiData.forecast_sites}")

    def delete_sites(self, dataframe:pd.DataFrame, print_is_requested:bool=True) -> None:
        """
        TODO
        """
        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError('dataframe must be a Pandas DataFrame.')

        for _, row in dataframe.iterrows():
            site_id = row['site_id']
            # TODO CHECK DATAFRAME STRUCTURE

            ApiRequester.get_site_delete(site_id, print_is_requested=print_is_requested)

        if print_is_requested:
            print(f"Requested sites have been deleted: \n {ApiData.forecast_sites}")

    def delete_all_sites(self, print_is_requested:bool=True) -> None:
        """
        TODO
        """
        for _, row in ApiData.forecast_sites.iterrows():
            # TODO CHECK DATAFRAME STRUCTURE

            site_id = row['site_id']
            ApiRequester.get_site_delete(site_id, print_is_requested=print_is_requested)
        
        if print_is_requested:
            print(f"All sites have been deleted: \n {ApiData.forecast_sites}")