import requests
import os

def obtener_lat_lng_desde_direccion(direccion):
    try:
        API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={direccion}&key={API_KEY}"
        response = requests.get(url)
        data = response.json()
        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
    except Exception as e:
        print("❌ Error geocodificando dirección:", e)
    return None, None


def verificar_cobertura_por_coordenadas(lat, lng):
    try:
        url = f"http://equipos_red:5004/cajas-nap/disponible-cercana?lat={lat}&lng={lng}"
        res = requests.get(url)
        return res.status_code == 200
    except Exception as e:
        print("❌ Error al verificar cobertura:", e)
        return False
