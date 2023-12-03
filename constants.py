# Created by Giacomo Mastroddi August 2023

ROUTE = '..\\ss_offline_data\\route\\BWSC\\route_preprocessed.csv'
CONTROL_STOPS = '..\\ss_offline_data\\route\\BWSC\\control_stops.csv'
CAMPING = '..\\ss_offline_data\\route\\BWSC\\mygeodata\\preprocessed\\Camping.csv'
TIMEZONE = 'Australia/Darwin'
GEO = {
    'latitude':     {'min': -90.0, 'max': 90.0},
    'longitude':    {'min': -180.0, 'max': 180.0}
}
TOKEN_MAPBOX = 'pk.eyJ1IjoiamFja21hc3Rybzk5IiwiYSI6ImNsbm1qeTN3bjJiOG8yc25zNzdzZzdqMTYifQ.UNq25l3Vhx3aEZDcHd35iw'
MAX_SITES_NUMBER_METEOTEST = 150
MAX_SITES_NUMBER_SOLCAST = 1500
KEY_METEOTEST = '6C985B9DF101FF63EB494A0FF420FCA6'
KEY_SOLCAST = '8nlT1zxKs9TFihx0V54jmkpnMjnVyTcD'
FORECAST_PARAMETERS_METEOTEST = {
    'tt':   {'unit': '°C',     'description': 'Air Temperature'},
    'gh':   {'unit': 'W/m2',   'description': 'Global radiation on the horizontal plane'},
    'dh':   {'unit': 'W/m2',   'description': 'Diffuse radiation on the horizontal plane'},
    'bh':   {'unit': 'W/m2',   'description': 'Direct radiation on the horizontal plane'},
    'gk':   {'unit': 'W/m2',   'description': 'Global radiation on the inclined plane'},
    'dni':  {'unit': 'W/m2',   'description': 'Direct normal irradiation'},
    'e':    {'unit': 'Wh/kWp', 'description': 'Energy output'},
    'rr':   {'unit': 'mm',     'description': 'Precipitation'},
    'rh':   {'unit': '%',      'description': 'Relative humidity'},
    'ff':   {'unit': 'km/h',   'description': 'Wind speed'},
    'dd':   {'unit': 'Degree', 'description': 'Wind direction'},
    'fx':   {'unit': 'km/h',   'description': 'Wind gust'},
    'qff':  {'unit': 'hPa',    'description': 'Mean sea level pressure'},
    'tcc':  {'unit': 'octa',   'description': 'Total cloud coverage'},
    'hdd':  {'unit': '°C',     'description': 'Heating degree days'},
    'cdd':  {'unit': '°C',     'description': 'Cooling degree days'}
}
FORECAST_PARAMETERS_SOLCAST = {
    'air_temp':             {'unit': '°C',    'description': 'Air Temperature'},
    'albedo':               {'unit': '0 - 1', 'description': 'Albedo Daily'},
    'azimuth':              {'unit': '°',     'description': 'Solar Azimuth Angle'},
    'clearsky_dhi':         {'unit': 'W/m2',  'description': 'Clearsky Diffuse Horizontal Irradiance (DHI)'},
    'clearsky_dni':         {'unit': 'W/m2',  'description': 'Clearsky Direct Normal Irradiance (DNI)'},
    'clearsky_ghi':         {'unit': 'W/m2',  'description': 'Clearsky Global Horizontal Irradiance (GHI)'},
    'clearsky_gti':         {'unit': 'W/m2',  'description': 'Clearsky Global Tilted Irradiance (GTI)'},
    'cloud_opacity':        {'unit': '%',     'description': 'Cloud Opacity'},
    'cloud_opacity10':      {'unit': '%',     'description': 'Cloud Opacity - 10th'},
    'cloud_opacity90':      {'unit': '%',     'description': 'Cloud Opacity - 90th'},
    'dewpoint_temp':        {'unit': '°C',    'description': 'Dewpoint Temperature'},
    'dhi':                  {'unit': 'W/m2',  'description': 'Diffuse Horizontal Irradiance (DHI)'},
    'dhi10':                {'unit': 'W/m2',  'description': 'Diffuse Horizontal Irradiance (DHI) - 10th'},
    'dhi90':                {'unit': 'W/m2',  'description': 'Diffuse Horizontal Irradiance (DHI) - 90th'},
    'dni':                  {'unit': 'W/m2',  'description': 'Direct Normal Irradiance (DNI)'},
    'dni10':                {'unit': 'W/m2',  'description': 'Direct Normal Irradiance (DNI) - 10th'},
    'dni90':                {'unit': 'W/m2',  'description': 'Direct Normal Irradiance (DNI) - 90th'},
    'ghi':                  {'unit': 'W/m2',  'description': 'Global Horizontal Irradiance (GHI)'},
    'ghi10':                {'unit': 'W/m2',  'description': 'Global Horizontal Irradiance (GHI) - 10th'},
    'ghi90':                {'unit': 'W/m2',  'description': 'Global Horizontal Irradiance (GHI) - 90th'},
    'gti':                  {'unit': 'W/m2',  'description': 'Global Tilted Irradiance (GTI)'},
    'gti10':                {'unit': 'W/m2',  'description': 'Global Tilted Irradiance (GTI) - 10th'},
    'gti90':                {'unit': 'W/m2',  'description': 'Global Tilted Irradiance (GTI) - 90th'},
    'precipitable_water':   {'unit': 'kg/m2', 'description': 'Precipitable Water'},
    'precipitation_rate':   {'unit': 'mm/h',  'description': 'Precipitation Rate'},
    'relative_humidity':    {'unit': '%',     'description': 'Relative Humidity'},
    'surface_pressure':     {'unit': 'hPa',   'description': 'Surface Pressure'},
    'snow_depth':           {'unit': 'cm',    'description': 'Snow Depth'},
    'snow_soiling_rooftop': {'unit': '%',     'description': 'Snow Soiling Loss - Rooftop'},
    'snow_soiling_ground':  {'unit': '%',     'description': 'Snow Soiling Loss - Ground Mounted'},
    'snow_water_equivalent':{'unit': 'cm',    'description': 'Snow water equivalent'},
    'wind_direction_100m':  {'unit': '°',     'description': 'Wind Direction 100m'},
    'wind_direction_10m':   {'unit': '°',     'description': 'Wind Direction 10m'},
    'wind_speed_100m':      {'unit': 'm/s',   'description': 'Wind Speed 100m'},
    'wind_speed_10m':       {'unit': 'm/s',   'description': 'Wind Speed 10m'},
    'zenith':               {'unit': '°',     'description': 'Solar Zenith Angle'}
}
