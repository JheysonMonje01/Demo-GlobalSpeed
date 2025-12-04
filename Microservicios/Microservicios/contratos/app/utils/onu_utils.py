import os
import requests

ONUS_SERVICE_URL = os.getenv("ONUS_SERVICE_URL", "http://localhost:5004")  # Ajusta el puerto si es distinto

def obtener_datos_onu(id_onu):
    try:
        url = f"{ONUS_SERVICE_URL}/onus/{id_onu}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()
        if not isinstance(data, dict) or "id_onu" not in data:
            return {"error": "La ONU no existe o los datos son inválidos."}
       
        return data

    except requests.RequestException as e:
        return {"error": f"Error al obtener datos de la ONU: {str(e)}"}        
