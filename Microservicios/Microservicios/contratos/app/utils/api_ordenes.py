# app/utils/api_ordenes.py
import requests
import os
import logging

ORDENES_SERVICE_URL = os.getenv("ORDENES_SERVICE_URL")

def crear_orden_instalacion(id_contrato):
    url = f"{ORDENES_SERVICE_URL}/ordenes_instalacion"
    payload = {"id_contrato": id_contrato}
    try:
        response = requests.post(url, json=payload)
        if response.status_code in [200, 201]:
            logging.info(f"✅ Orden de instalación creada para contrato {id_contrato}")
            return True, response.json()
        else:
            logging.warning(f"⚠️ Falló la creación de la orden para contrato {id_contrato}: {response.text}")
            return False, response.text
    except Exception as e:
        logging.error(f"❌ Error al comunicar con servicio de órdenes: {str(e)}")
        return False, str(e)
