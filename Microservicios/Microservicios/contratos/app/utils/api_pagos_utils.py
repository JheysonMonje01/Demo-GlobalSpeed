import os
import requests

PAGOS_SERVICE_URL = os.getenv("PAGOS_SERVICE_URL", "http://pagos:5008")

def notificar_creacion_orden_pago(id_contrato, id_plan, fecha_inicio):
    try:
        url = f"{PAGOS_SERVICE_URL}/orden_pago/crear"
        payload = {
            "id_contrato": id_contrato,
            "id_plan": id_plan,
            "fecha_inicio": fecha_inicio  # en formato ISO
        }

        response = requests.post(url, json=payload)

        if response.status_code == 201:
            return {
                "status": "success",
                "message": "Órdenes de pago creadas correctamente",
                "data": response.json()
            }
        else:
            return {
                "status": "error",
                "message": f"Error al crear órdenes de pago",
                "detalle": response.text
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Excepción al contactar servicio de pagos: {str(e)}"
        }
