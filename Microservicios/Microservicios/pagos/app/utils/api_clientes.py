import requests
import os

CLIENTE_URL = os.getenv("CLIENTES_SERVICE_URL", "http://clientes:5001")

# app/utils/api_clientes.py
def get_cliente_por_id(id_cliente):
    try:
        r = requests.get(f"{CLIENTE_URL}/clientes/{id_cliente}")
        if r.ok:
            return {"status": "success", "cliente": r.json()}
        else:
            return {"status": "error", "message": r.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}
