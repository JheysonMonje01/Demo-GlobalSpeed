import requests
import os

def geocode_direccion(direccion):
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={direccion}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        return None, None
