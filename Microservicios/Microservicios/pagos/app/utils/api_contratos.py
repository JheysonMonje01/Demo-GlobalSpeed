import requests
import os

CONTRATO_URL = os.getenv("CONTRATO_SERVICE_URL", "http://contratos:5006")


def get_contrato_por_id(id_contrato):
    try:
        res = requests.get(f"{CONTRATO_URL}/contratos/{id_contrato}")
        if res.ok:
            return {"status": "success", "contrato": res.json()}
        else:
            return {"status": "error", "message": f"Contrato no encontrado: {res.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}