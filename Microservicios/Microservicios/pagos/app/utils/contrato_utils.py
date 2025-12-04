import os
import requests

CONTRATO_SERVICE_URL = os.getenv("CONTRATO_SERVICE_URL", "http://contratos:5006")

def obtener_datos_contrato(id_contrato):
    try:
        url = f"{CONTRATO_SERVICE_URL}/contratos/{id_contrato}"
        response = requests.get(url)
        if response.status_code != 200:
            return {"status": "error", "message": "Error al obtener contrato", "detalle": response.text}

        data = response.json()
        return data

    except Exception as e:
        return {"status": "error", "message": f"Excepción al consultar contrato: {str(e)}"}


