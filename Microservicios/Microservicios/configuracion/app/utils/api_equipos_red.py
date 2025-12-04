import os
import requests

EQUIPOS_RED_URL = os.getenv("EQUIPOS_RED_SERVICE_URL", "http://equipos_red:5004")

def obtener_datos_olt(id_olt):
    try:
        url = f"{EQUIPOS_RED_URL}/olts/{id_olt}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"❌ Error al obtener OLT: {e}")
        return None
