import os
import requests

INSTALACIONES_URL = os.getenv("INSTALACIONES_SERVICE_URL", "http://instalaciones_service:5010")


def obtener_orden_por_contrato(id_contrato):
    try:
        url = f"{INSTALACIONES_URL}/ordenes_instalacion/por-contrato/{id_contrato}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None
