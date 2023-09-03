import pandas as pd
from api_requester import ApiRequester

class ApiExecuter():
    """
    TODO
    """

    def __init__(self, requester:ApiRequester) -> None:
        self.requester = requester

    def add_sites(self, dataframe:pd.DataFrame, print_is_requested:bool=True) -> None:
        """
        TODO
        """
        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError('dataframe must be a Pandas DataFrame.')
        # TODO CHECK DATAFRAME STRUCTURE
        
        count = 0
        for _, row in dataframe.iterrows():
            name = str(count)
            latitude = row['latitude']
            longitude = row['longitude']

            self.requester.get_site_add(name=name, latitude=latitude, longitude=longitude, print_is_requested=print_is_requested)
            count += 1

        if print_is_requested:
            print(f"Requested sites have been added: \n {self.requester.forecast_sites}")

    def delete_sites(self, dataframe:pd.DataFrame, print_is_requested:bool=True) -> None:
        """
        TODO
        """
        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError('dataframe must be a Pandas DataFrame.')
        # TODO CHECK DATAFRAME STRUCTURE

        for site_id in dataframe.index:
            self.requester.get_site_delete(site_id, print_is_requested=print_is_requested)

            self.requester.get_site_delete(site_id, print_is_requested=print_is_requested)

        if print_is_requested:
            print(f"Requested sites have been deleted: \n {self.requester.forecast_sites}")

    def delete_all_sites(self, print_is_requested:bool=True) -> None:
        """
        TODO
        """
        for site_id in self.requester.forecast_sites.index:
            print(self.requester.forecast_sites.index)
            self.requester.get_site_delete(site_id, print_is_requested=print_is_requested)
        
        if print_is_requested:
            print(f"All sites have been deleted: \n {self.requester.forecast_sites}")