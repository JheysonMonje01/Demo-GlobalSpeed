import os
import requests

# Variables de entorno
CONTRATO_SERVICE_URL = os.getenv("CONTRATO_SERVICE_URL", "http://contratos:5006")
PLANES_SERVICE_URL = os.getenv("PLANES_SERVICE_URL", "http://planes_internet:5005")
EQUIPOS_RED_SERVICE_URL = os.getenv("EQUIPOS_RED_SERVICE_URL", "http://equipos_red:5004")
CONFIGURACION_SERVICE_URL = os.getenv("CONFIGURACION_SERVICE_URL", "http://configuracion:5002")


def obtener_contrato(id_contrato):
    try:
        res = requests.get(f"{CONTRATO_SERVICE_URL}/contratos/{id_contrato}", timeout=10)
        return res.json() if res.ok else None
    except Exception as e:
        print(f"Error al obtener contrato: {e}")
        return None


def obtener_plan(id_plan):
    try:
        res = requests.get(f"{PLANES_SERVICE_URL}/planes/{id_plan}", timeout=10)
        return res.json() if res.ok else None
    except Exception as e:
        print(f"Error al obtener plan: {e}")
        return None


def obtener_pool_por_nombre(nombre_pool):
    try:
        res = requests.get(f"{EQUIPOS_RED_SERVICE_URL}/pools", timeout=10)
        if res.ok:
            for pool in res.json():
                if pool["nombre"] == nombre_pool:
                    return pool
        return None
    except Exception as e:
        print(f"Error al obtener pool: {e}")
        return None


def crear_perfil_en_mikrotik(data):
    """ Usado para crear perfil PPPoE (POST) """
    try:
        res = requests.post(f"{CONFIGURACION_SERVICE_URL}/mikrotik/crear-perfil-pppoe", json=data, timeout=10)
        return res.ok, res.json()
    except Exception as e:
        return False, {"message": f"Error al crear perfil PPPoE: {str(e)}"}


def actualizar_perfil_en_mikrotik(data):
    """ Usado para actualizar perfil PPPoE (PUT) """
    try:
        res = requests.put(f"{CONFIGURACION_SERVICE_URL}/mikrotik/actualizar-perfil-pppoe", json=data, timeout=10)
        return res.ok, res.json()
    except Exception as e:
        return False, {"message": f"Error al actualizar perfil PPPoE: {str(e)}"}
