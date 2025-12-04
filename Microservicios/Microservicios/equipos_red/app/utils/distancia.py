import requests
import os
from dotenv import load_dotenv

load_dotenv()

def obtener_distancia_google_maps(origen_lat, origen_lng, destino_lat, destino_lng):
    API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")  # define en tu .env
    endpoint = "https://maps.googleapis.com/maps/api/distancematrix/json"

    params = {
        "origins": f"{origen_lat},{origen_lng}",
        "destinations": f"{destino_lat},{destino_lng}",
        "key": API_KEY,
        "mode": "walking"  # o 'walking' si prefieres a pie
    }

    response = requests.get(endpoint, params=params)
    data = response.json()

    if data["status"] == "OK":
        distancia_metros = data["rows"][0]["elements"][0]["distance"]["value"]
        return distancia_metros / 1000  # Convertimos a KM
    else:
        raise Exception(f"Error en Google Maps API: {data}")
