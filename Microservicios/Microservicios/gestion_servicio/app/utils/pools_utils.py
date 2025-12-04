import os
import requests
import ipaddress
from app.models.usuario_pppoe_model import UsuarioPPPoE

EQUIPOS_RED_SERVICE_URL = os.getenv("EQUIPOS_RED_SERVICE_URL", "http://equipos_red:5004")
CONTRATOS_SERVICE_URL = os.getenv("CONTRATOS_SERVICE_URL", "http://contratos:5006")


def obtener_datos_pool_por_nombre(nombre_pool):
    try:
        url = f"{EQUIPOS_RED_SERVICE_URL}/pools/nombre/{nombre_pool}"
        response = requests.get(url)

        if response.status_code != 200:
            return {
                "status": "error",
                "message": "No se pudo obtener el pool por nombre",
                "detalle": response.text
            }

        return response.json()  # ya contiene status y pool

    except Exception as e:
        return {
            "status": "error",
            "message": f"Excepción al consultar el pool: {str(e)}"
        }


def obtener_ip_libre_en_pool(rango_inicio, rango_fin):
    try:
        ip_inicio = ipaddress.IPv4Address(rango_inicio)
        ip_fin = ipaddress.IPv4Address(rango_fin)

        ips_ocupadas = {
            str(ip.ip_remota) for ip in UsuarioPPPoE.query.all() if ip.ip_remota
        }

        for ip in range(int(ip_inicio), int(ip_fin) + 1):
            actual = str(ipaddress.IPv4Address(ip))
            if actual == ip_inicio or actual == ip_inicio + 1 or actual == ip_fin:
                continue
            if str(actual) not in ips_ocupadas:
                return str(actual)
        return None

    except Exception as e:
        return None


def obtener_onu_por_contrato(id_contrato):
    try:
        url = f"{EQUIPOS_RED_SERVICE_URL}/onus/contrato/{id_contrato}"
        response = requests.get(url)

        if response.status_code != 200:
            return {
                "status": "error",
                "message": "No se pudo obtener la ONU",
                "detalle": response.text
            }

        return {
            "status": "success",
            "onu": response.json()
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Excepción al consultar la ONU: {str(e)}"
        }
import logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def obtener_datos_red_por_contrato(id_contrato):
    try:
        
        
        # 1. Obtener contrato para obtener id_cliente
        url_contrato = f"{CONTRATOS_SERVICE_URL}/contratos/{id_contrato}"
        resp_contrato = requests.get(url_contrato)
        if resp_contrato.status_code != 200:
            return {"status": "error", "message": "No se pudo obtener el contrato", "detalle": resp_contrato.text}
        contrato = resp_contrato.json()
        id_cliente = contrato.get("id_cliente")
        logging.info(f"[🔎 DEBUG] id_cliente obtenido: {id_cliente}")
        
        # 1. Obtener ONU
        url_onu = f"{EQUIPOS_RED_SERVICE_URL}/onus/contrato/{id_contrato}"
        resp_onu = requests.get(url_onu)

        if resp_onu.status_code != 200:
            return {"status": "error", "message": "No se pudo obtener la ONU", "detalle": resp_onu.text}

        onu = resp_onu.json()
        serial = onu.get("serial")
        ont_id = onu.get("ont_id")
        id_puerto_pon_olt = onu.get("id_puerto_pon_olt")

        # 2. Obtener Puerto PON
        url_puerto = f"{EQUIPOS_RED_SERVICE_URL}/puertos/{id_puerto_pon_olt}"
        resp_puerto = requests.get(url_puerto)

        if resp_puerto.status_code != 200:
            return {"status": "error", "message": "No se pudo obtener el puerto PON", "detalle": resp_puerto.text}

        puerto = resp_puerto.json()
        numero_puerto = puerto.get("numero_puerto")
        id_tarjeta_olt = puerto.get("id_tarjeta_olt")

        # 3. Obtener Tarjeta OLT
        url_tarjeta = f"{EQUIPOS_RED_SERVICE_URL}/tarjetas-olt/{id_tarjeta_olt}"
        resp_tarjeta = requests.get(url_tarjeta)

        if resp_tarjeta.status_code != 200:
            return {"status": "error", "message": "No se pudo obtener la tarjeta OLT", "detalle": resp_tarjeta.text}

        tarjeta = resp_tarjeta.json()
        slot_numero = tarjeta.get("slot_numero")
        id_olt = tarjeta.get("id_olt")

        # 4. Calcular frame
        frame = id_olt - 1 if isinstance(id_olt, int) else None

        return {
            "status": "success",
            "datos": {
                "serial": serial,
                "ont_id": ont_id,
                "numero_puerto": numero_puerto,
                "slot_numero": slot_numero,
                "frame": frame,
                "id_olt": id_olt,
                "id_cliente": id_cliente  # ✅ finalmente aquí
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Excepción al obtener datos de red: {str(e)}"
        }


def obtener_vlan_por_id(id_vlan):
    try:
        url = f"{EQUIPOS_RED_SERVICE_URL}/api/vlan/{id_vlan}"  # ✅ CORREGIDO aquí
        response = requests.get(url)

        if response.status_code != 200:
            return None

        return response.json()

    except Exception as e:
        return None

def actualizar_estado_onu(id_onu, nuevo_estado):
    try:
        url = f"{EQUIPOS_RED_SERVICE_URL}/onus/{id_onu}/estado"
        payload = {"estado": nuevo_estado}
        response = requests.put(url, json=payload, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Error al actualizar estado de la ONU: {str(e)}"}
    
def obtener_onu_por_contrato(id_contrato):
    try:
        url = f"{EQUIPOS_RED_SERVICE_URL}/onus/contrato/{id_contrato}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Error al obtener ONU por contrato: {str(e)}"}