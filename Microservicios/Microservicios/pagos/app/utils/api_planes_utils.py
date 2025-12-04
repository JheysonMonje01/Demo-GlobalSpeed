import os
import requests

PLANES_SERVICE_URL = os.getenv("PLANES_SERVICE_URL", "http://planes_internet:5005")

def obtener_datos_plan(id_plan):
    try:
        url = f"{PLANES_SERVICE_URL}/planes/{id_plan}"
        response = requests.get(url)

        if response.status_code != 200:
            return {
                "status": "error",
                "message": f"Error HTTP {response.status_code}",
                "detalle": response.text
            }

        data = response.json()
        return {"status": "success", "plan": data}

    except Exception as e:
        return {
            "status": "error",
            "message": f"Excepción al obtener el plan: {str(e)}"
        }
