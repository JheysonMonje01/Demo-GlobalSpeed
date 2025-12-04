'''from app.models.onu import ONU
from app.models.caja_nap import CajaNAP
from app.models.puerto_pon_olt import PuertoPONOLT
from app.extensions import db
from flask import abort
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# 🔹 Crear ONU
def crear_onu(data):
    try:
        id_caja = data.get("id_caja")
        id_puerto = data.get("id_puerto_pon_olt")

        # Validaciones
        if not CajaNAP.query.get(id_caja):
            abort(404, description="Caja NAP no encontrada")

        if not PuertoPONOLT.query.get(id_puerto):
            abort(404, description="Puerto PON OLT no encontrado")

        # Validar puerto disponible
        numero_puerto_nap = data.get("numero_puerto_nap")
        existente = ONU.query.filter_by(id_caja=id_caja, numero_puerto_nap=numero_puerto_nap).first()
        if existente:
            abort(400, description=f"El puerto {numero_puerto_nap} ya está ocupado en esta caja")

        nueva_onu = ONU(**data)
        db.session.add(nueva_onu)

        # Actualizar puertos ocupados
        caja = CajaNAP.query.get(id_caja)
        caja.puertos_ocupados = ONU.query.filter_by(id_caja=id_caja).count() + 1

        db.session.commit()
        return nueva_onu

    except SQLAlchemyError as e:
        db.session.rollback()
        abort(500, description=f"Error al registrar la ONU: {str(e)}")

# 🔹 Obtener todas las ONUs (con filtros opcionales)
def listar_onus(filtros=None):
    query = ONU.query
    if filtros:
        if "estado" in filtros:
            query = query.filter_by(estado=filtros["estado"])
        if "id_caja" in filtros:
            query = query.filter_by(id_caja=filtros["id_caja"])
        if "id_contrato" in filtros:
            query = query.filter_by(id_contrato=filtros["id_contrato"])
    return query.all()

# 🔹 Obtener ONU por ID
def obtener_onu(id_onu):
    onu = ONU.query.get(id_onu)
    if not onu:
        abort(404, description="ONU no encontrada")
    return onu

# 🔹 Actualizar ONU
def actualizar_onu(id_onu, data):
    onu = ONU.query.get(id_onu)
    if not onu:
        abort(404, description="ONU no encontrada")

    id_caja_nueva = data.get("id_caja", onu.id_caja)
    puerto_nuevo = data.get("numero_puerto_nap", onu.numero_puerto_nap)

    if id_caja_nueva != onu.id_caja or puerto_nuevo != onu.numero_puerto_nap:
        existente = ONU.query.filter_by(id_caja=id_caja_nueva, numero_puerto_nap=puerto_nuevo).first()
        if existente and existente.id_onu != id_onu:
            abort(400, description=f"El puerto {puerto_nuevo} ya está ocupado en la caja {id_caja_nueva}")

    onu.id_caja = id_caja_nueva
    onu.serial_number = data.get("serial_number", onu.serial_number)
    onu.ont_id = data.get("ont_id", onu.ont_id)
    onu.modelo_onu = data.get("modelo_onu", onu.modelo_onu)
    onu.numero_puerto_nap = puerto_nuevo
    onu.id_puerto_pon_olt = data.get("id_puerto_pon_olt", onu.id_puerto_pon_olt)
    onu.id_contrato = data.get("id_contrato", onu.id_contrato)
    onu.estado = data.get("estado", onu.estado)
    onu.fecha_modificacion = datetime.utcnow()

    db.session.commit()

    # Actualizar ocupación
    for caja_id in {onu.id_caja, id_caja_nueva}:
        caja = CajaNAP.query.get(caja_id)
        if caja:
            caja.puertos_ocupados = ONU.query.filter_by(id_caja=caja_id).count()
    db.session.commit()

    return onu

# 🔹 Eliminar ONU

def eliminar_onu(id_onu, logico=True):
    onu = ONU.query.get(id_onu)
    if not onu:
        abort(404, description="ONU no encontrada")

    if logico:
        onu.estado = False
    else:
        db.session.delete(onu)

    # Actualizar puertos ocupados
    caja = CajaNAP.query.get(onu.id_caja)
    if caja:
        caja.puertos_ocupados = ONU.query.filter_by(id_caja=onu.id_caja, estado=True).count()

    db.session.commit()
    return {"mensaje": "ONU eliminada correctamente"}

from app.models.caja_nap import CajaNAP

def registrar_onu_detectada(data):
    try:
        id_caja = data.get("id_caja")  # puede ser None
        numero_puerto_nap = data.get("numero_puerto_nap")  # puede ser None

        if id_caja is not None:
            caja = CajaNAP.query.get(id_caja)
            if not caja:
                abort(404, description="Caja NAP no encontrada")

            if numero_puerto_nap is not None:
                existente = ONU.query.filter_by(
                    id_caja=id_caja,
                    numero_puerto_nap=numero_puerto_nap
                ).first()
                if existente:
                    abort(400, description="Puerto NAP ya ocupado en esa caja")

        id_puerto_pon_olt = data.get("id_puerto_pon_olt")
        if not PuertoPONOLT.query.get(id_puerto_pon_olt):
            abort(404, description="Puerto PON no encontrado")

        if ONU.query.filter_by(serial_number=data["serial_number"]).first():
            abort(400, description="Ya existe una ONU con este serial")

        duplicada = ONU.query.filter_by(
            id_puerto_pon_olt=id_puerto_pon_olt,
            ont_id=str(data["ont_id"])
        ).first()
        if duplicada:
            abort(400, description="El ont_id ya está ocupado en ese puerto PON")

        nueva_onu = ONU(
            serial_number=data["serial_number"],
            modelo_onu=data["modelo_onu"],
            ont_id=str(data["ont_id"]),
            numero_puerto_nap=numero_puerto_nap,
            id_caja=id_caja,
            id_puerto_pon_olt=id_puerto_pon_olt,
            id_contrato=data.get("id_contrato"),
        )

        db.session.add(nueva_onu)

        if id_caja:
            caja.puertos_ocupados = ONU.query.filter_by(id_caja=id_caja).count()

        db.session.commit()
        return nueva_onu

    except SQLAlchemyError as e:
        db.session.rollback()
        abort(500, description=f"Error en base de datos: {str(e)}")


def deducir_puerto_pon_desde_caja(id_caja):
    caja = CajaNAP.query.get(id_caja)
    if not caja:
        abort(404, description="Caja NAP no encontrada")

    if not caja.id_puerto_pon_olt:
        abort(400, description="Caja NAP no tiene puerto PON asignado")

    return caja.id_puerto_pon_olt

def actualizar_onu_existente(onu, datos_actualizados):
    if not onu:
        raise ValueError("ONU no encontrada")

    if "id_caja" in datos_actualizados:
        onu.id_caja = datos_actualizados["id_caja"]

    if "numero_puerto_nap" in datos_actualizados:
        onu.numero_puerto_nap = datos_actualizados["numero_puerto_nap"]

    if "id_puerto_pon_olt" in datos_actualizados:
        onu.id_puerto_pon_olt = datos_actualizados["id_puerto_pon_olt"]

    db.session.commit()
    return onu'''

from app.models.onu import ONU
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from sqlalchemy import or_
from app.models.onu import ONU
from app.extensions import db

#REGISTRAR ONUS COMO SI FUERA INVENTARIO SOLO SERIAL OPCIONAL MODELO
def registrar_onu(data):
    try:
        # `data` ya es una instancia de ONU, no un diccionario
        serial = data.serial
        modelo_onu = data.modelo_onu

        # Verificar duplicado por serial
        existente = ONU.query.filter_by(serial=serial).first()
        if existente:
            return {
                "status": "error",
                "message": "Ya existe una ONU con ese número de serie."
            }, 409

        # Estado por defecto (por si no vino en el JSON)
        data.estado = data.estado or 'libre'
        data.fecha_creacion = datetime.utcnow()

        db.session.add(data)
        db.session.commit()

        return {
            "status": "success",
            "message": "ONU registrada correctamente.",
            "onu": data.id_onu
        }, 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return {
            "status": "error",
            "message": f"Error en base de datos: {str(e)}"
        }, 500

# Listar todas las ONUs
def listar_onus():
    try:
        onus = ONU.query.all()
        return onus, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500


# Obtener ONU por ID
def obtener_onu_por_id(id_onu):
    onu = ONU.query.get(id_onu)
    if not onu:
        return {"status": "error", "message": "ONU no encontrada."}, 404
    return onu, 200

# Actualizar serial o modelo_onu
def actualizar_onu(id_onu, data):
    try:
        onu = ONU.query.get(id_onu)
        if not onu:
            return {"status": "error", "message": "ONU no encontrada."}, 404

        nuevo_serial = data.get("serial")
        nuevo_modelo = data.get("modelo_onu")

        # Validar duplicado si el serial cambió
        if nuevo_serial and nuevo_serial != onu.serial:
            if ONU.query.filter_by(serial=nuevo_serial).first():
                return {"status": "error", "message": "Ya existe una ONU con ese serial."}, 409
            onu.serial = nuevo_serial

        if nuevo_modelo:
            onu.modelo_onu = nuevo_modelo

        db.session.commit()

        return {"status": "success", "message": "ONU actualizada correctamente."}, 200

    except Exception as e:
        db.session.rollback()
        return {"status": "error", "message": f"Error al actualizar ONU: {str(e)}"}, 500


# Eliminar ONU
def eliminar_onu(id_onu):
    try:
        onu = ONU.query.get(id_onu)
        if not onu:
            return {"status": "error", "message": "ONU no encontrada."}, 404

        db.session.delete(onu)
        db.session.commit()

        return {"status": "success", "message": "ONU eliminada correctamente."}, 200

    except Exception as e:
        db.session.rollback()
        return {"status": "error", "message": f"Error al eliminar ONU: {str(e)}"}, 500
    
#filtros

def filtrar_onus(filtro_texto=None, estado=None):
    try:
        query = ONU.query

        if filtro_texto:
            texto = f"%{filtro_texto.lower()}%"
            query = query.filter(
                or_(
                    db.func.lower(ONU.serial).like(texto),
                    db.func.lower(ONU.modelo_onu).like(texto)
                )
            )

        if estado:
            query = query.filter_by(estado=estado)

        onus = query.all()
        return onus, 200

    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

import logging
# Asignar una ONU a un contrato y generar ont_id único
### PASO 1: Crear archivo "services/onu_service.py" si no existe

def asignar_onu_a_contrato(id_onu, id_contrato, caja):
    try:
        logging.info(f"🔧 Buscando ONU con id {id_onu}")
        onu = ONU.query.get(id_onu)
        if not onu:
            return False, "ONU no encontrada"

        if onu.estado != "libre":
            return False, "ONU ya está asignada"

        numero_puerto_nap = caja.puertos_ocupados + 1
        logging.info(f"ℹ️ Puerto NAP asignado: {numero_puerto_nap}")

        ont_id_existentes = ONU.query.filter_by(id_puerto_pon_olt=caja.id_puerto_pon_olt).with_entities(ONU.ont_id).all()
        ids_usados = [int(ont[0]) for ont in ont_id_existentes if ont[0] is not None]  # <--- aquí
        ont_id = max(ids_usados, default=0) + 1
        logging.info(f"ℹ️ ONT ID asignado: {ont_id}")

        onu.id_contrato = id_contrato
        onu.id_caja = caja.id_caja
        onu.id_puerto_pon_olt = caja.id_puerto_pon_olt
        onu.numero_puerto_nap = numero_puerto_nap
        onu.ont_id = ont_id
        onu.estado = "asignado"

        caja.puertos_ocupados = numero_puerto_nap

        db.session.commit()
        logging.info("✅ ONU y Caja actualizadas correctamente en la base de datos")
        return True, "ONU asignada correctamente"

    except Exception as e:
        db.session.rollback()
        logging.exception("❌ Error al asignar ONU a contrato")
        return False, str(e)

def obtener_onu_por_contrato(id_contrato):
    try:
        return ONU.query.filter_by(id_contrato=id_contrato).first()
    except Exception as e:
        return None
    
#actualizar estado onu
def actualizar_estado_onu(id_onu, nuevo_estado):
    onu = ONU.query.get(id_onu)
    if not onu:
        return {"status": "error", "message": "ONU no encontrada"}, 404

    onu.estado = nuevo_estado
    db.session.commit()

    return {"status": "success", "message": "Estado de la ONU actualizado correctamente", "onu": {
        "id_onu": onu.id_onu,
        "estado": onu.estado
    }}, 200