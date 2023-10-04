import folium
import pandas as pd

class Plotter():
    """ """
    def __init__(self, route_data) -> None:
        #TODO PER GENERALIZZARLO PRENDERE "PUNTO MEDIO" DEI PUNTI IN ROUTE

        # Create a base map centered around Australia
        self.map = folium.Map(location=[-25.2744, 133.7751],
                              zoom_start=0)

        # Define the bounds
        min_lng = route_data['longitude'].min()
        min_lat = route_data['latitude'].min()
        max_lng = route_data['longitude'].max()
        max_lat = route_data['latitude'].max()
        bounds = [[max_lat, min_lng], [min_lat, max_lng]]
        self.map.fit_bounds(bounds)

        self.map.options['maxBounds'] = bounds
        self.map.options['maxBoundsViscosity'] = 0.9
        self.map.options['minZoom'] = 5

        folium.PolyLine(
        locations=route_data[['latitude', 'longitude']].values.tolist(),
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
                popup=row['name']
            ).add_to(self.map)
    
    def add_control_stops(self, control_stops_df:pd.DataFrame) -> None:
        """ """
        for _, row in control_stops_df.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=3,
                color="orange",
                fill=True,
                fill_color="orange",
                fill_opacity=1,
                popup=row['location']
            ).add_to(self.map)

    def add_current_position(self, current_position) -> None:
        """ """
        folium.CircleMarker(
                location=[current_position['latitude'], current_position['longitude']],
                radius=3,
                color="red",
                fill=True,
                fill_color="red",
                fill_opacity=1,
                popup="You"
            ).add_to(self.map)