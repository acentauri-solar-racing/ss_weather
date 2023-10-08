import dash
import dash_leaflet as dl
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
from route import Route

# Initialize the Dash app
app = dash.Dash(__name__)

class PlotterDash():
    def __init__(self, route:Route) -> None:
        self.route = route
        self.route_data = self.route.get_route_data
        self.control_stops = pd.DataFrame()  # Consider possibility of not having control stops
        self.start_position = None
        self.end_position = None

    def get_dash_map(self):
        # Create a base map centered around the middle of the route
        middle_lat = self.route_data['latitude'].mean()
        middle_lng = self.route_data['longitude'].mean()

        # Create route line
        path = [dl.Polyline(positions=self.route_data[['latitude', 'longitude']].values.tolist(), color="green")]

        # Add API sites (assuming you have a method to get them)
        # sites = self.get_api_sites()
        # for site in sites:
        #     path.append(dl.Marker(position=(site['latitude'], site['longitude']), children=dl.Tooltip(site['name'])))

        # Add control stops
        for _, row in self.control_stops.iterrows():
            path.append(dl.Marker(position=(row['latitude'], row['longitude']), children=dl.Tooltip(row['town'] + ': ' + row['location'])))

        # Return the map
        return dl.Map(center=(middle_lat, middle_lng), zoom=10, children=path)

# Create an instance of the Plotter class
plotter = PlotterDash(route=Route())  # Assuming you have a Route instance

# Define the layout of the Dash app
app.layout = html.Div([
    plotter.get_dash_map(),
    # Add other components like sliders, graphs, etc. here
])

# Define callbacks to update components based on user interactions
# Example:
@app.callback(
    Output('your-output-component-id', 'property-to-update'),
    [Input('your-input-component-id', 'property-to-listen-to')]
)
def update_output(input_value):
    # Your update logic here
    return 'Output: {}'.format(input_value)

if __name__ == '__main__':
    app.run_server(debug=True)
