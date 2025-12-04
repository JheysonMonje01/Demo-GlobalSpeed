import requests
import os

def post_configuracion(endpoint, data):
    try:
        URL_BASE = os.getenv("CONFIGURACION_SERVICE_URL", "http://configuracion:5002")
        url = f"{URL_BASE}{endpoint}"
        response = requests.post(url, json=data, timeout=10)

        if response.status_code in [200, 201]:
            return True, response.json().get("message", "Éxito")
        else:
            return False, response.json().get("message", "Error en la petición")

    except requests.exceptions.ConnectionError:
        return False, "No se pudo conectar con el microservicio de configuración"
    except requests.exceptions.Timeout:
        return False, "Tiempo de espera agotado al conectar con configuración"
    except Exception as e:
        return False, f"Error inesperado al conectar: {str(e)}"

# ✅ GET usado para validar existencia de MikroTik
def get_configuracion(endpoint):
    try:
        URL_BASE = os.getenv("CONFIGURACION_SERVICE_URL", "http://configuracion:5002")
        url = f"{URL_BASE}{endpoint}"
        response = requests.get(url, timeout=10)
        


        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json().get("message", "No encontrado")

    except requests.exceptions.ConnectionError:
        return False, "No se pudo conectar con el microservicio de configuración"
    except requests.exceptions.Timeout:
        return False, "Tiempo de espera agotado al conectar con configuración"
    except Exception as e:
        return False, f"Error inesperado al conectar: {str(e)}"

def verificar_mikrotik_existe(id_mikrotik):
    return get_configuracion(f"/mikrotik/configuraciones/{id_mikrotik}")
