import geocoder
import numpy as np
import pandas as pd
import constants

def get_current_location() -> dict:
    """ Get current location using geocoder. """

    g = geocoder.ip('me')  # 'me' corresponds to your current IP address
    if g.latlng:
        latitude, longitude = g.latlng
        return {'latitude': latitude, 'longitude': longitude}
    else:
        raise ValueError('Could not find your location. Please check your internet connection.')
    
def rad2deg(rad:float) -> float:
    """ Convert radians to degrees. """
    return rad * 180 / np.pi

def get_race_time() -> pd.Timestamp:
    """ """
    now = pd.Timestamp.now(tz=constants.TIMEZONE)
    current_hour = now.hour
    
    if current_hour <= 17 and current_hour >= 8:
        # During the race
        return now

    elif current_hour > 17:
        # At night
        return now + pd.DateOffset(days=1, hour=8, minute=0, second=0, microsecond=0, nanosecond=0)

    elif current_hour < 8:
        # At morning
        return now.replace(hour=8, minute=0, second=0, microsecond=0, nanosecond=0)


# from geopy.geocoders import Nominatim

# def get_current_location():
#     """ Get current location using geopy. """
#     # Initialize a geocoder with Nominatim (OpenStreetMap) provider
#     geolocator = Nominatim(user_agent="my_geocoder")

#     # Get the current location using the geolocator
#     location = geolocator.geocode("")

#     if location:
#         latitude = location.latitude
#         longitude = location.longitude
#         return latitude, longitude
#     else:
#         print("Location not found.")
#         return None, None

# latitude, longitude = get_current_location()
# if latitude is not None and longitude is not None:
#     print(f"Latitude: {latitude}, Longitude: {longitude}")
