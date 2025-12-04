import requests
import os

def get_vlan_por_id(id_vlan):
    """
    Realiza una petición al microservicio de equipos_red para obtener información de la VLAN por su ID.
    """
    try:
        url_base = os.getenv("EQUIPOS_RED_SERVICE_URL", "http://equipos_red:5004")
        url = f"{url_base}/api/vlan/{id_vlan}"

        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            return True, response.json()
        elif response.status_code == 404:
            return False, f"No se encontró la VLAN con id {id_vlan}"
        else:
            return False, f"Error en la petición: {response.json().get('message', 'Error desconocido')}"

    except requests.exceptions.ConnectionError:
        return False, "No se pudo conectar con el microservicio de equipos_red"
    except requests.exceptions.Timeout:
        return False, "Tiempo de espera agotado al conectar con equipos_red"
    except Exception as e:
        return False, f"Error inesperado al conectar con equipos_red: {str(e)}"
