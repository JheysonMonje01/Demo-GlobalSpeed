import requests
import os

CONTRATO_SERVICE_URL = os.getenv("CONTRATO_SERVICE_URL", "http://contratos:5006")
CLIENTE_SERVICE_URL = os.getenv("CLIENTE_SERVICE_URL", "http://clientes:5001")

def obtener_contrato_por_id(id_contrato):
    try:
        res = requests.get(f"{CONTRATO_SERVICE_URL}/contratos/{id_contrato}", timeout=5)
        if res.ok:
            return res.json()
    except:
        pass
    return None

def obtener_nombre_completo_cliente(id_cliente):
    try:
        res = requests.get(f"{CLIENTE_SERVICE_URL}/clientes/{id_cliente}", timeout=5)
        if res.ok:
            cliente = res.json()
            persona = cliente.get("persona", {})
            nombre = persona.get("nombre", "")
            apellido = persona.get("apellido", "")
            return f"{nombre} {apellido}"
    except:
        pass
    return None
