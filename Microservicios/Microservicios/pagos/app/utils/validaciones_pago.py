from decimal import Decimal
from app.models.orden_pago_model import OrdenPago

def validar_pago_transferencia(data, file):
    errores = {}

    if not data.get("id_contrato"):
        errores["id_contrato"] = "El contrato es obligatorio."

    if not data.get("id_metodo_pago"):
        errores["id_metodo_pago"] = "El método de pago es obligatorio."

    try:
        monto = Decimal(str(data.get("monto", "0")))
        if monto <= 0:
            errores["monto"] = "El monto debe ser positivo."
    except:
        errores["monto"] = "Monto inválido. Debe ser numérico."

    # ✅ Validar existencia y estado de la orden de pago
    id_orden = data.get("id_orden_pago")
    if not id_orden:
        errores["id_orden_pago"] = "Debe proporcionar la orden de pago."
    else:
        orden = OrdenPago.query.get(id_orden)
        if not orden:
            errores["id_orden_pago"] = "La orden de pago no existe."
        else:
            if orden.estado not in ["pendiente", "vencido"]:
                errores["id_orden_pago"] = f"No se puede pagar una orden con estado: {orden.estado}"
            if orden.id_contrato != int(data.get("id_contrato")):
                errores["id_orden_pago"] = "La orden no pertenece al contrato indicado."
            if orden.id_pago:
                errores["id_orden_pago"] = "La orden ya tiene un pago asignado."

    if not file:
        errores["comprobante"] = "Debe adjuntar una imagen del comprobante."

    return errores
