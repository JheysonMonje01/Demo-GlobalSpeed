import os
import requests

CONFIGURACION_SERVICE_URL = os.getenv("CONFIGURACION_SERVICE_URL", "http://localhost:5002")

def obtener_datos_empresa():
    try:
        url = f"{CONFIGURACION_SERVICE_URL}/api/empresa"
        response = requests.get(url)
        if response.status_code == 200:
            datos = response.json()
            if datos:
                return datos[0]  # tomamos la primera empresa
            return None
        return None
    except Exception as e:
        print(f"❌ Error al obtener datos de empresa: {str(e)}")
        return None
