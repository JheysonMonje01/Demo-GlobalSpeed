import os
import requests
from app.extensions import logger

AUTENTICACION_SERVICE_URL = os.getenv("AUTENTICACION_SERVICE_URL", "http://autenticacion:5000")

def obtener_correo_usuario_por_id(id_usuario):
    url = f"{AUTENTICACION_SERVICE_URL}/auth/usuarios/{id_usuario}"
    logger.info(f"📡 Consultando usuario: {url}")
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data["usuario"]["correo"]
        else:
            logger.info(f"❌ Error al obtener usuario: {response.text}")
            return None
    except Exception as e:
        logger.info(f"❌ Error al conectar con autenticacion: {e}")
        return None