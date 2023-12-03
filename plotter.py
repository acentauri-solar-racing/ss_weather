# Created by Giacomo Mastroddi October 2023

import folium
import pandas as pd
from route import Route

class Plotter():
    """ Class to plot the route and the current position in a folium map."""

    def __init__(self, route:Route) -> None:
        self.route = route
        self.route_data = self.route.get_route_data
        self.control_stops = pd.DataFrame() # Consider possibility of not having control stops
        self.start_position = None
        self.end_position = None

        min_lng = self.route_data['longitude'].min()
        min_lat = self.route_data['latitude'].min()
        max_lng = self.route_data['longitude'].max()
        max_lat = self.route_data['latitude'].max()

        # Create a base map centered around the midle of the route
        middle_lat = (max_lat + min_lat) / 2
        middle_lng = (max_lng + min_lng) / 2
        self.map = folium.Map(
                        location=[middle_lat, middle_lng],
                        zoom_start=0
                    )

        # Define the bounds
        bounds = [[max_lat, min_lng], [min_lat, max_lng]]
        self.map.fit_bounds(bounds)

        self.map.options['maxBounds'] = bounds
        self.map.options['maxBoundsViscosity'] = 0.9
        self.map.options['minZoom'] = 5

        folium.PolyLine(
            locations=self.route_data[['latitude', 'longitude']].values.tolist(),
            color="green",
            weight=4,
            opacity=1
        ).add_to(self.map)

    @property
    def plot(self) -> None:
        """ Plot the map."""
        return self.map
    
    def add_api_sites(self, api_sites:pd.DataFrame) -> None:
        """ Add the API sites of forecasts to the map."""
        for _, row in api_sites.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=2,
                color="blue",
                fill=True,
                fill_color="blue",
                fill_opacity=1,
                tooltip=row['name']
            ).add_to(self.map)
    
    def add_control_stops(self, control_stops_df:pd.DataFrame) -> None:
        """ Add the control stops to the map."""
        # Save control stops dataframe without first and last row
        self.control_stops = control_stops_df.iloc[1:-1]
        self.start_position = control_stops_df.iloc[0]
        self.end_position = control_stops_df.iloc[-1]

        for _, row in control_stops_df.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=3,
                color="orange",
                fill=True,
                fill_color="orange",
                fill_opacity=1,
                tooltip=row['town'] + ': ' + row['location']
            ).add_to(self.map)

    def add_current_position(self, current_position:dict) -> None:
        """ Add the current position to the map."""
        folium.Marker(
                location=[current_position['latitude'], current_position['longitude']],
                icon=folium.Icon(icon="car", prefix="fa"),  # Using Font Awesome's car icon
                popup="Current Location"
        ).add_to(self.map)

    #     icon_image = "URL_TO_YOUR_CAR_IMAGE.png"  # Replace with your image URL
    # icon = folium.CustomIcon(icon_image, icon_size=(30, 30))  # Adjust icon_size as needed
    
    # folium.Marker(
    #     location=[lat, lng],
    #     icon=icon,
    #     popup="Current Location"
    # ).add_to(map_obj)

    def _recursive_position_finder(self, current_cumDistance:float, driving_time:float, cs_to_skip:int) -> pd.Series:
        """ Recursively find the position at the end of the driving time considering the control stops."""
        # Cut data at current position (lower cut)
        cut_data = self.route_data.copy()

        cut_data = cut_data[cut_data['cumDistance'] >= current_cumDistance]
        cut_data = cut_data.reset_index(drop=True)

        current_time = cut_data['cumTimeAtMaxSpeedLim'][0]

        # Cut data at driving time (upper cut)
        cut_data = cut_data[cut_data['cumTimeAtMaxSpeedLim'] <= current_time + driving_time]
        max_cumDistance = cut_data['cumDistance'].max()

        # Check if the control stop dataframe is not empty
        if not self.control_stops.empty:
            cs_in_range_mask = (self.control_stops['cumDistance'] >= current_cumDistance) & (self.control_stops['cumDistance'] <= max_cumDistance)
            cs_in_range = cs_in_range_mask.sum()
            print(f'cs found ahead: {cs_in_range}')
            print(f'cs to skip: {cs_to_skip}')
        else:
            print("No control stop dataframe given")

        # Stop cases
        # Reach end of route, return last point
        if current_cumDistance >= self.route_data.iloc[-1]['cumDistance']:
            return self.route_data.iloc[-1] # return self.end_position
        
        # All control stops considered
        if cs_to_skip == cs_in_range:
            print("All control stops considered")
            return self.route_data.loc[self.route_data['cumDistance'] == max_cumDistance].iloc[0]
        
        # Stop at control stop for the night, meaning we arrive at cs between 16:30 and 17:00
        if cs_to_skip > cs_in_range:
            print("Stop at control stop for the night")
            return self.control_stops.loc[self.control_stops['cumDistance'] > current_cumDistance].iloc[cs_to_skip - 1]
        

        # Recursive call to skip control stop and reduce driving time by 30 minutes
        if cs_to_skip < cs_in_range: # Case of 0 cs in range considered
            print("--- Recursive call ---")
            return self._recursive_position_finder(current_cumDistance, driving_time - 30.0*60.0, cs_to_skip + 1)
        
    def update_max_speed_distance(self, current_position:dict) -> float:
        """ Add the position that will be reached at the end of the day considering driving at max speed."""
        # Subtract overnight stop start time to now
        now = pd.Timestamp.now()
        driving_time = pd.Timedelta(hours=17) - pd.Timedelta(hours=now.hour, minutes=now.minute)
        current_cumDistance = self.route.find_closest_row(current_position, print_is_requested=False)[0]['cumDistance']

        position_series = self._recursive_position_finder(current_cumDistance, driving_time.total_seconds(), cs_to_skip=0)

        folium.RegularPolygonMarker(
            location=[position_series['latitude'], position_series['longitude']],
            number_of_sides=3,
            radius=5,
            color="red",
            fill=True,
            fill_color="red",
            fill_opacity=1,
            popup="Max speed distance"
        ).add_to(self.map)

        return position_series['cumDistance']