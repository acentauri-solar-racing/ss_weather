import folium

class Plotter():
    def __init__(self, route_data) -> None:
        #TODO PER GENERALIZZARLO PRENDERE "PUNTO MEDIO" DEI PUNTI IN ROUTE

        # Create a base map centered around Australia
        self.map = folium.Map(location=[-25.2744, 133.7751], min_zoom=5, max_bounds=True)

        # Define the bounds
        bounds = [[-35, 125], [-12, 140]]
        self.map.fit_bounds(bounds)

    def 

control_stops_df = route_data.get_control_stops_data
sites_df = api_requester.get_current_sites

# Add the route lines
rt = route_data.get_route_data
folium.PolyLine(
    locations=rt[['latitude', 'longitude']].values.tolist(),
    color="green",
    weight=4,
    opacity=1
).add_to(map)

# Add api sites
for _, row in sites_df.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=2,
        color="blue",
        fill=True,
        fill_color="blue",
        fill_opacity=1,
        popup=row['name']
    ).add_to(map)

# Add control stops
for _, row in control_stops_df.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=3,
        color="orange",
        fill=True,
        fill_color="orange",
        fill_opacity=1,
        popup=row['location']
    ).add_to(map)

map
