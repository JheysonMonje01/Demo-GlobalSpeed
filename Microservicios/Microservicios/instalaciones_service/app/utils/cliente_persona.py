import os
import requests

CLIENTES_SERVICE_URL = os.getenv("CLIENTES_SERVICE_URL", "http://localhost:5001")

def obtener_datos_cliente(id_cliente):
    try:

         # Paso 1: Obtener el cliente por ID
        url_cliente = f"{CLIENTES_SERVICE_URL}/clientes/{id_cliente}"
        response_cliente = requests.get(url_cliente, timeout=5)
        response_cliente.raise_for_status()
        cliente_data = response_cliente.json()

        id_persona = cliente_data.get("id_persona")
        if not id_persona:
            return {"error": f"No se encontró 'id_persona' para el cliente con ID {id_cliente}"}
        
        # Paso 2: Obtener los datos de la persona con el id_persona
        url_persona = f"{CLIENTES_SERVICE_URL}/api/personas-filtros?id_persona={id_persona}"
        response_persona = requests.get(url_persona, timeout=5)
        response_persona.raise_for_status()
        data = response_persona.json()

        if isinstance(data, dict) and "nombres" in data:
            return data

        if isinstance(data, list) and len(data) > 0:
            return data[0]

        return {"error": f"Persona con ID {id_persona} no encontrada o datos inválidos"}


    except requests.RequestException as e:
        return {"error": f"Error al conectar con el microservicio de clientes: {str(e)}"}
