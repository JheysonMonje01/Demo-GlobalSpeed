import os
import requests

CONFIGURACION_SERVICE_URL = os.getenv("CONFIGURACION_SERVICE_URL", "http://localhost:5002")

def obtener_datos_empresa(id_empresa):
    try:
        url = f"{CONFIGURACION_SERVICE_URL}/api/empresa?id_empresa={id_empresa}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        # ⚠️ Validación de tipo de respuesta
        if isinstance(data, list):
            if not data:
                return {"error": "Empresa no encontrada."}
            return data[0]  # ✅ Retornar el primer elemento de la lista

        if not isinstance(data, dict):
            return {"error": "La respuesta de empresa no contiene datos válidos."}

        return data

    except requests.RequestException as e:
        return {"error": f"Error al obtener datos de empresa: {str(e)}"}
