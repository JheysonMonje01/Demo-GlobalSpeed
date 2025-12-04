from app.models.caja_nap import CajaNAP
from app.models.onu import ONU
from app.models.puerto_pon_olt import PuertoPONOLT
from app.extensions import db
from flask import abort
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# 🔹 Crear caja NAP
def crear_caja_nap(caja: CajaNAP):
    try:
        if not isinstance(caja.capacidad_puertos_cliente, int) or caja.capacidad_puertos_cliente <= 0:
            abort(400, description="La capacidad debe ser un número entero positivo.")

        puerto = PuertoPONOLT.query.get(caja.id_puerto_pon_olt)
        if not puerto:
            abort(404, description="Puerto PON OLT no encontrado.")

        caja.puertos_ocupados = 0
        db.session.add(caja)
        db.session.commit()
        return caja

    except SQLAlchemyError as e:
        db.session.rollback()
        abort(500, description=f"Error al crear la caja: {str(e)}")

# 🔹 Obtener todas las cajas NAP (con filtros opcionales)
def obtener_cajas_nap(filtros=None):
    query = CajaNAP.query
    if filtros:
        if "estado" in filtros:
            estado = filtros["estado"].lower() == "true"
            query = query.filter_by(estado=estado)
        if "id_puerto_pon_olt" in filtros:
            query = query.filter_by(id_puerto_pon_olt=int(filtros["id_puerto_pon_olt"]))
    return query.all()

# 🔹 Obtener una caja por ID
def obtener_caja_por_id(id_caja):
    caja = CajaNAP.query.get(id_caja)
    if not caja:
        abort(404, description="Caja NAP no encontrada.")
    return caja

# 🔹 Actualizar una caja NAP
def actualizar_caja_nap(id_caja, data: CajaNAP):
    caja = CajaNAP.query.get(id_caja)
    if not caja:
        abort(404, description="Caja NAP no encontrada.")

    # Validar puerto si se quiere cambiar
    if data.id_puerto_pon_olt and data.id_puerto_pon_olt != caja.id_puerto_pon_olt:
        puerto = PuertoPONOLT.query.get(data.id_puerto_pon_olt)
        if not puerto:
            abort(404, description="Nuevo puerto PON OLT no encontrado.")
        caja.id_puerto_pon_olt = data.id_puerto_pon_olt

    # Validar capacidad
    if data.capacidad_puertos_cliente is not None:
        if not isinstance(data.capacidad_puertos_cliente, int) or data.capacidad_puertos_cliente <= 0:
            abort(400, description="La capacidad debe ser un número entero positivo.")
        caja.capacidad_puertos_cliente = data.capacidad_puertos_cliente

    # Asignar otros campos
    caja.nombre_caja_nap = data.nombre_caja_nap or caja.nombre_caja_nap
    caja.ubicacion = data.ubicacion or caja.ubicacion
    caja.latitud = data.latitud or caja.latitud
    caja.longitud = data.longitud or caja.longitud
    caja.observacion = data.observacion or caja.observacion
    caja.radio_cobertura = data.radio_cobertura or caja.radio_cobertura
    caja.estado = data.estado if data.estado is not None else caja.estado
    caja.fecha_modificacion = datetime.utcnow()

    db.session.commit()
    return caja

# 🔹 Eliminar caja NAP (lógico o físico)
def eliminar_caja_nap(id_caja, logico=True):
    caja = CajaNAP.query.get(id_caja)
    if not caja:
        abort(404, description="Caja NAP no encontrada.")

    if logico:
        caja.estado = False
    else:
        db.session.delete(caja)
    
    db.session.commit()
    return {"mensaje": "Caja eliminada correctamente."}

# 🔹 Recalcular puertos ocupados según las ONUs asignadas
def actualizar_puertos_ocupados(id_caja):
    caja = CajaNAP.query.get(id_caja)
    if not caja:
        abort(404, description="Caja NAP no encontrada.")

    ocupados = ONU.query.filter_by(id_caja=id_caja, estado=True).count()
    caja.puertos_ocupados = ocupados
    caja.fecha_modificacion = datetime.utcnow()
    db.session.commit()
