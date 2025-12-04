# app/utils/api_contratos.py
import os
import requests

def verificar_contratos_activos(id_plan):
    try:
        contratos_service_url = os.getenv("CONTRATOS_SERVICE_URL", "http://contratos:5006")
        url = f"{contratos_service_url}/contratos/plan/{id_plan}/asociaciones"

        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return False, f"Error al consultar contratos asociados: {response.json().get('message', 'Respuesta inválida')}"

        data = response.json()
        return data["en_uso"], data.get("ids_contratos", [])

    except Exception as e:
        return False, f"Error de conexión al microservicio de contratos: {str(e)}"



