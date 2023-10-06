import folium
import pandas as pd

class Plotter():
    """ """
    def __init__(self, route_data) -> None:
        self.route_data = route_data
        self.control_stops = pd.DataFrame()

        # Create a base map centered around Australia
        middle_lat = (max_lat - min_lat) / 2
        middle_lng = (max_lng - min_lng) / 2
        self.map = folium.Map(
                        location=[middle_lat, middle_lng],
                        zoom_start=0
                    )

        # Define the bounds
        min_lng = self.route_data['longitude'].min()
        min_lat = self.route_data['latitude'].min()
        max_lng = self.route_data['longitude'].max()
        max_lat = self.route_data['latitude'].max()
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
    
    def add_weather_sites(self, api_sites:pd.DataFrame) -> None:
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
        self.control_stops = control_stops_df

        for _, row in control_stops_df.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=3,
                color="orange",
                fill=True,
                fill_color="orange",
                fill_opacity=1,
                tooltip=row['location']
            ).add_to(self.map)

    def add_current_position(self, current_position) -> None:
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

    def _recursive_index_finder(self, driving_time:float, control_stop_to_skip:int) -> int:
        """ """
        
        # Stop case

        
    def update_max_speed_distance(self) -> float:
        """ """
        #TODO considerare fine della gara per cui non ha senso pensare al os: se idx supera limite dare fine gara e print
        #TODO nella ricerca togliere partenza e arrivo per la ricerca di cs
        #TODO sapendo che cs dura 30 min, non togliere 30 min se mancano 30 min alle 17, ma si rimane nel cs

        # Subtract overnight stop start time to now
        now = pd.Timestamp.now()
        driving_time = pd.Timedelta(hours=17) - pd.Timedelta(hours=now.hour, minutes=now.minute)

        
        idx_lat = self.route_data.iloc[idx]['latitude']
        idx_lng = self.route_data.iloc[idx]['longitude']

        folium.CircleMarker(
                location=[idx_lat, idx_lng],
                radius=3,
                color="red",
                fill=True,
                fill_color="red",
                fill_opacity=1,
                popup="You"
            ).add_to(self.map)
        
        return distance_left