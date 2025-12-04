import os
import requests

CONTRATO_SERVICE_URL = os.getenv("CONTRATO_SERVICE_URL", "http://localhost:5006")  # Ajusta el puerto si es distinto

def obtener_datos_contrato(id_contrato):
    try:
        url = f"{CONTRATO_SERVICE_URL}/contratos/{id_contrato}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()
        if not isinstance(data, dict) or "id_contrato" not in data:
            return {"error": "El Contrato no existe o los datos son inválidos."}
       
        return data

    except requests.RequestException as e:
        return {"error": f"Error al obtener datos del Contrato: {str(e)}"}     