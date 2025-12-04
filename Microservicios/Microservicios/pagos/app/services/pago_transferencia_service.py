import os
from datetime import datetime
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError
from app.models.pago_model import Pago
from app.extensions import db
from app.utils.validaciones_pago import validar_pago_transferencia
from app.config import Config


def guardar_archivo_transferencia(file, id_pago):
    try:
        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".pdf"]:
            return None, "Formato no permitido. Solo se aceptan imágenes o PDF."

        # Ruta absoluta para guardar el archivo
        carpeta_absoluta = os.path.join(Config.DIRECTORIO_COMPROBANTES, str(id_pago))
        os.makedirs(carpeta_absoluta, exist_ok=True)

        ruta_absoluta = os.path.join(carpeta_absoluta, filename)
        file.save(ruta_absoluta)

        # Ruta relativa que se guarda en la DB
        ruta_relativa = f"comprobantes/{id_pago}/{filename}"
        return ruta_relativa, None

    except Exception as e:
        return None, f"Error al guardar archivo: {str(e)}"


from app.utils.contrato_utils import obtener_datos_contrato

def registrar_pago_transferencia(data, file):
    try:
        errores = validar_pago_transferencia(data, file)
        if errores:
            return {"error": errores}, 400

        from app.models.orden_pago_model import OrdenPago  # evitar import circular

        id_orden_pago = int(data.get("id_orden_pago"))
        id_contrato = int(data.get("id_contrato"))

        # Verificar existencia del contrato con microservicio
        contrato = obtener_datos_contrato(id_contrato)
        if not contrato or contrato.get("status") == "error":
            return {"error": {"id_contrato": "El contrato no existe o no se pudo verificar."}}, 400

        # Obtener orden de pago
        orden = OrdenPago.query.get(id_orden_pago)
        if not orden:
            return {"error": {"id_orden_pago": "La orden de pago no existe."}}, 400

        # Validar estado de la orden
        estado_orden = orden.estado.strip().lower() if orden.estado else ""
        if estado_orden not in ["pendiente", "vencido"]:
            return {"error": {"id_orden_pago": "La orden no está pendiente ni vencida."}}, 400

        # Validar contrato asociado a la orden
        if orden.id_contrato != id_contrato:
            return {"error": {"id_orden_pago": "La orden no pertenece al contrato indicado."}}, 400

        # Verificar que aún no tenga pago asignado
        if orden.id_pago is not None:
            return {"error": {"id_orden_pago": "La orden ya tiene un pago asignado."}}, 400

        # Crear el pago
        nuevo_pago = Pago(
            id_contrato=id_contrato,
            id_metodo_pago=data["id_metodo_pago"],
            monto=data["monto"],
            mes_correspondiente=orden.mes_correspondiente,
            observacion=data.get("observacion", "").strip(),
            estado=False,
            fecha_creacion=datetime.utcnow()
        )

        db.session.add(nuevo_pago)
        db.session.flush()  # Obtener ID

        # Guardar comprobante
        ruta_comprobante, error_archivo = guardar_archivo_transferencia(file, nuevo_pago.id_pago)
        if error_archivo:
            db.session.rollback()
            return {"error": {"comprobante": error_archivo}}, 400

        nuevo_pago.comprobante = ruta_comprobante

        # Actualizar orden
        orden.estado = "cancelado"
        orden.fecha_pago = datetime.utcnow()
        orden.id_pago = nuevo_pago.id_pago

        db.session.commit()
        return nuevo_pago, 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": f"Error al registrar pago en base de datos: {str(e)}"}, 500
    except Exception as e:
        db.session.rollback()
        return {"error": f"Error inesperado: {str(e)}"}, 500


def actualizar_comprobante_pago(id_pago, file):
    try:
        pago = Pago.query.get(id_pago)
        if not pago:
            return {"error": "Pago no encontrado."}, 404

        if not file:
            return {"error": "Debe adjuntar un comprobante."}, 400

        ruta, error = guardar_archivo_transferencia(file, id_pago)
        if error:
            return {"error": error}, 400

        pago.comprobante = ruta
        pago.fecha_modificacion = datetime.utcnow()
        db.session.commit()

        return pago, 200

    except SQLAlchemyError:
        db.session.rollback()
        return {"error": "Error al actualizar el comprobante."}, 500
    except Exception as e:
        db.session.rollback()
        return {"error": f"Error inesperado: {str(e)}"}, 500
