import os
import requests

CLIENTES_SERVICE_URL = os.getenv("CLIENTES_SERVICE_URL", "http://localhost:5001")

def obtener_datos_tecnico(id_tecnico):
    try:

         # Paso 1: Obtener el cliente por ID
        url_tecnico = f"{CLIENTES_SERVICE_URL}/tecnicos/{id_tecnico}"
        response_tecnico = requests.get(url_tecnico, timeout=5)
        response_tecnico.raise_for_status()
        tecnico_data = response_tecnico.json()

        id_persona = tecnico_data.get("id_persona")
        if not id_persona:
            return {"error": f"No se encontró 'id_persona' para el cliente con ID {id_tecnico}"}
        
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

def obtener_tecnico_activo():
    try:
        url = f"{CLIENTES_SERVICE_URL}/tecnicos?estado=activo"
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        tecnicos = response.json()

        if isinstance(tecnicos, list) and len(tecnicos) > 0:
            return tecnicos[0]  # Puedes cambiar la lógica si deseas seleccionar el más libre
        else:
            return None  # No hay técnicos activos

    except requests.RequestException as e:
        print(f"❌ Error al obtener técnicos activos: {str(e)}")
        return None
    
def actualizar_estado_tecnico(id_tecnico, nuevo_estado):
    try:
        url = f"{CLIENTES_SERVICE_URL}/tecnicos/{id_tecnico}/estado"
        response = requests.put(url, json={"estado": nuevo_estado}, timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"❌ Error al actualizar estado del técnico: {e}")
        return False