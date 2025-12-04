# utils/api_config.py
import requests
import os

def post_configuracion(endpoint, data):
    """
    Envía una solicitud POST al microservicio de configuración.
    """
    try:
        url_base = os.getenv("CONFIGURACION_SERVICE_URL", "http://configuracion:5002")
        url = f"{url_base}{endpoint}"

        response = requests.post(url, json=data, timeout=10)

        if response.status_code in [200, 201]:
            return True, response.json().get("message", "Éxito")
        else:
            return False, response.json().get("message", "Error en la petición")

    except Exception as e:
        return False, f"Error al conectar con el microservicio de configuración: {str(e)}"


