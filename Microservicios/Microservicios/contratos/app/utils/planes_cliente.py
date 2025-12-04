import os
import requests

PLANES_SERVICE_URL = os.getenv("PLANES_SERVICE_URL", "http://localhost:5005")

def obtener_datos_plan(id_plan):
    try:
        url = f"{PLANES_SERVICE_URL}/planes/{id_plan}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()

        # ✅ Validar que data es un diccionario y tenga campos clave
        if not isinstance(data, dict) or "nombre_plan" not in data:
            return {"error": "No se encontró el plan o la respuesta es inválida."}

        return data

    except requests.RequestException as e:
        return {"error": f"Error al obtener datos del plan: {str(e)}"}
