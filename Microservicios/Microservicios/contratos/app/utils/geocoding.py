# utils/geocoding.py
import os
import requests

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def obtener_direccion_desde_coordenadas(lat, lng):
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "latlng": f"{lat},{lng}",
            "key": GOOGLE_MAPS_API_KEY,
            "language": "es"
        }

        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data["status"] == "OK" and data["results"]:
            return data["results"][0]["formatted_address"]
        else:
            return "Ubicación no encontrada"

    except Exception as e:
        return "Ubicación no encontrada"
