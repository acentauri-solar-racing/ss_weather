import geocoder

def get_current_location() -> tuple:
    """
    Get current location using geocoder.
    """
    g = geocoder.ip('me')  # 'me' corresponds to your current IP address
    if g.latlng:
        latitude, longitude = g.latlng
        return latitude, longitude
    else:
        raise ValueError('Could not find your location. Please check your internet connection.')
    
# from geopy.geocoders import Nominatim

# def get_current_location():
#     """
#     Get current location using geopy.
#     """
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
