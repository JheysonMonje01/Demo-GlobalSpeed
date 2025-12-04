# app/services/puerto_tarjeta_service.py

from app.models.puerto_pon_olt import PuertoPONOLT
from app.models.tarjeta_olt import TarjetaOLT
from app.extensions import db
from flask import abort

def listar_puertos(id_tarjeta_olt=None):
    if id_tarjeta_olt is not None:
        return PuertoPONOLT.query.filter_by(id_tarjeta_olt=id_tarjeta_olt).all()
    return PuertoPONOLT.query.all()


def obtener_puerto(id_puerto):
    return PuertoPONOLT.query.get(id_puerto)

def crear_puerto(data):
    id_tarjeta = data.get("id_tarjeta_olt")
    tarjeta = TarjetaOLT.query.get(id_tarjeta)
    if not tarjeta:
        abort(404, description="Tarjeta OLT no encontrada")

    # Validar capacidad
    puertos_actuales = PuertoPONOLT.query.filter_by(id_tarjeta_olt=id_tarjeta).count()
    if puertos_actuales >= tarjeta.capacidad:
        abort(400, description="Capacidad máxima de puertos alcanzada para esta tarjeta OLT")

    # Asignar automáticamente el siguiente número de puerto disponible
    puertos_usados = [p.numero_puerto for p in PuertoPONOLT.query.filter_by(id_tarjeta_olt=id_tarjeta).all()]
    numero_puerto = next((i for i in range(tarjeta.capacidad) if i not in puertos_usados), puertos_actuales)

    nuevo_puerto = PuertoPONOLT(
        id_tarjeta_olt=id_tarjeta,
        numero_puerto=numero_puerto,
        estado_puerto=data.get("estado_puerto", True)
    )
    db.session.add(nuevo_puerto)

    # Actualizar ocupados
    tarjeta.actualizar_puertos_ocupados()
    db.session.commit()
    return nuevo_puerto


def actualizar_puerto(id_puerto, data):
    puerto = PuertoPONOLT.query.get(id_puerto)
    if not puerto:
        abort(404, description="Puerto no encontrado")

    # Solo se permite cambiar estado u otros datos simples, pero no el número
    estado = data.get("estado_puerto")
    if estado is not None:
        puerto.estado_puerto = estado

    db.session.commit()
    return puerto


def eliminar_puerto(id_puerto):
    puerto = PuertoPONOLT.query.get(id_puerto)
    if not puerto:
        abort(404, description="Puerto no encontrado")

    tarjeta = puerto.tarjeta
    db.session.delete(puerto)
    db.session.commit()

    if tarjeta:
        tarjeta.actualizar_puertos_ocupados()

    return puerto
