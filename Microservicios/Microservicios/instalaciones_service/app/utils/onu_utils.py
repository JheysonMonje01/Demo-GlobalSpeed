import os
import requests

ONUS_SERVICE_URL = os.getenv("ONUS_SERVICE_URL", "http://localhost:5004")  # Ajusta el puerto si es distinto
EQUIPOS_RED_SERVICE_URL = os.getenv("EQUIPOS_RED_SERVICE_URL", "http://equipos_red:5004")

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

import logging
logger = logging.getLogger(__name__)

def obtener_onu_por_contrato(id_contrato):
    try:
        url = f"{EQUIPOS_RED_SERVICE_URL}/onus/contrato/{id_contrato}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        logging.warning(f"⚠️ Respuesta inesperada al obtener ONU: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        logging.error(f"❌ Error al obtener ONU por contrato {id_contrato}: {str(e)}")
        return None


def actualizar_estado_onu(id_onu, nuevo_estado):
    try:
        response = requests.put(
            f"{EQUIPOS_RED_SERVICE_URL}/onus/{id_onu}/estado",
            json={"estado": nuevo_estado}
        )
        return response.status_code == 200
    except Exception as e:
        return False