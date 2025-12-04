import os
import requests

CONFIG_SERVICE_URL = os.getenv("CONFIGURACION_SERVICE_URL", "http://configuracion:5002")

def put_configuracion_desactivar_pppoe(data):
    url = f"{CONFIG_SERVICE_URL}/mikrotik/pppoe/desactivar"
    try:
        response = requests.put(url, json=data, timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        return False, {
            "status": "error",
            "message": f"Error al desactivar usuario PPPoE: {str(e)}"
        }


def put_configuracion_activar_pppoe(data):
    url = f"{CONFIG_SERVICE_URL}/mikrotik/pppoe/activar"
    try:
        response = requests.put(url, json=data, timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        return False, {
            "status": "error",
            "message": f"Error al activar usuario PPPoE: {str(e)}"
        }
