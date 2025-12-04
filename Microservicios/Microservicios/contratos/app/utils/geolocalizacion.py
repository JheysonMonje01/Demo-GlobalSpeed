import os
import requests

def obtener_direccion_google(lat, lon):
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise EnvironmentError("API Key de Google Maps no encontrada")

    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    if data['status'] != 'OK' or not data['results']:
        return None

    componentes = data['results'][0]['address_components']

    parroquia = canton = provincia = None

    for c in componentes:
        if "administrative_area_level_3" in c["types"]:
            parroquia = c["long_name"]
        elif "administrative_area_level_2" in c["types"]:
            canton = c["long_name"]
        elif "administrative_area_level_1" in c["types"]:
            provincia = c["long_name"]

    return {
        "provincia": provincia,
        "canton": canton,
        "parroquia": parroquia
    }
