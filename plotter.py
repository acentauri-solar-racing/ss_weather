import folium
import pandas as pd
from route import Route

class Plotter():
    """ """
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
        middle_lat = (max_lat - min_lat) / 2
        middle_lng = (max_lng - min_lng) / 2
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
        """ """
        return self.map
    
    def add_api_sites(self, api_sites:pd.DataFrame) -> None:
        """ """
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
        """ """
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
        """ """
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

    def _recursive_position_finder(self, current_cumDistance:float, driving_time:float, control_stop_to_skip:int) -> pd.Series:
        """ """
        # Cut data at current position (lower cut)
        cut_data = self.route_data[self.route_data['cumDistance'].copy() >= current_cumDistance]
        cut_data = cut_data.reset_index(drop=True)
        print(cut_data)
        print(1)
        current_time = cut_data['cumTimeAtMaxSpeed'][0]

        # Cut data at driving time (upper cut)
        cut_data = cut_data['cumTimeAtMaxSpeed'] <= current_time + driving_time
        print(2)
        max_cumDistance = cut_data['cumDistance']
        print(max_cumDistance)

        # Check if the control stop dataframe is not empty
        control_stops_in_range = 0
        if not self.control_stops.empty:
            # Count number of control stop in range of cut data
            control_stops_in_range = self.control_stops['cumDistance'] >= current_cumDistance & (self.control_stops['cumDistance'] <= max_cumDistance)
        else:
            print("No control stop dataframe given")

        print(3)
        # Stop cases
        # Reach end of route, return last point
        if current_cumDistance >= self.route_data.iloc[-1]['cumDistance']:
            return self.route_data.iloc[-1]
            # return self.end_position
        
        # All control stops considered
        if control_stop_to_skip == control_stop_to_skip:
            return self.route_data.loc[self.route_data['cumDistance'] == max_cumDistance].iloc[0]
        
        # Stop at control stop for the night, meaning we arrive at cs between 16:30 and 17:00
        if control_stop_to_skip > control_stops_in_range:
            return self.control_stops.loc[self.control_stops['cumDistance'] > max_cumDistance].iloc[0]


        # Recursive call to skip control stop and reduce driving time by 30 minutes
        if control_stop_to_skip < control_stops_in_range: # Case of 0 cs in range considered
            return self._recursive_position_finder(current_cumDistance, driving_time - 30.0*60.0, control_stop_to_skip + 1)

        
    def update_max_speed_distance(self, current_position:dict) -> float:
        """ """
        # Subtract overnight stop start time to now
        now = pd.Timestamp.now()
        driving_time = pd.Timedelta(hours=17) - pd.Timedelta(hours=now.hour, minutes=now.minute)
        current_cumDistance = self.route.find_closest_row(current_position, print_is_requested=True)['cumDistance']

        position_series = self._recursive_position_finder(current_cumDistance, driving_time.total_seconds(), control_stop_to_skip=0)

        folium.CircleMarker(
            location=[position_series['latitude'], position_series['longitude']],
            radius=3,
            color="red",
            fill=True,
            fill_color="red",
            fill_opacity=1,
            popup="You"
        ).add_to(self.map)
        
        return position_series['cumDistance'] - current_cumDistance