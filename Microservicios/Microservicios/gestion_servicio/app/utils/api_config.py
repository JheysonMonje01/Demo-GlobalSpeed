import os
import requests

CONFIG_SERVICE_URL = os.getenv("CONFIGURACION_SERVICE_URL", "http://configuracion:5002")


def post_configuracion_crear_pppoe(payload):
    url = f"{CONFIG_SERVICE_URL}/mikrotik/crear-perfil-pppoe"
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        return False, {"error": str(e)}


def obtener_mikrotik_activa():
    url = f"{CONFIG_SERVICE_URL}/mikrotik/activa"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return {"status": "success", "mikrotik": response.json()}
        else:
            return {
                "status": "error",
                "message": "No se pudo obtener MikroTik activa",
                "detalle": response.text
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al consultar MikroTik activa: {str(e)}"
        }

def obtener_mikrotik_por_nombre(nombre_mikrotik):
    url = f"{CONFIG_SERVICE_URL}/mikrotik/nombre/{nombre_mikrotik}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return {"success": True, "config": response.json()}
        else:
            return {"success": False, "message": "No encontrado", "detalle": response.text}
    except Exception as e:
        return {"success": False, "message": f"Error de conexión: {str(e)}"}



import requests
import os

def delete_usuario_pppoe_en_mikrotik(data):
    try:
        url = f"{CONFIG_SERVICE_URL}/mikrotik/eliminar-usuario-pppoe"
        response = requests.delete(url, json=data, timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        return False, {
            "status": "error",
            "message": f"Error inesperado al eliminar usuario PPPoE: {str(e)}"
        }


def post_configuracion_comandos_ont(data):
    """
    Enviar los comandos de configuración ONT a la OLT Huawei a través del microservicio de configuración.
    """
    try:
        url = f"{CONFIG_SERVICE_URL}/olt/ejecutar-comandos-ont"
        response = requests.post(url, json=data, timeout=10)

        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        return False, {"error": f"Error de conexión: {str(e)}"}


import logging


def post_configuracion_trafico_pppoe(usuario_pppoe):
    url = f"{CONFIG_SERVICE_URL}/mikrotik/monitoreo/trafico"
    data = {"usuario_pppoe": usuario_pppoe}
    logging.info(f"📦 Datos enviados: {data}")
    logging.info(f"📡 Enviando solicitud de monitoreo a: {url}")
    try:
        response = requests.post(url, json=data, timeout=10)
        response_data = response.json()
        if response.status_code == 200:
            return response_data, 200  # Devuelve directamente el JSON
        else:
            return response_data, response.status_code
    except Exception as e:
        logging.exception("❌ Error al consultar tráfico en el microservicio de configuración")
        return {"status": "error", "message": f"Error al consultar tráfico: {str(e)}"}, 500