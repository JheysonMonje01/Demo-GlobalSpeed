from app.models.tarjeta_olt import TarjetaOLT
from app.models.olt import OLT
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from flask import abort
from app.models.puerto_pon_olt import PuertoPONOLT



def listar_tarjetas_olt():
    return TarjetaOLT.query.all()

def obtener_tarjeta_olt(id_tarjeta):
    return TarjetaOLT.query.get(id_tarjeta)

def crear_tarjeta_olt(data):
    id_olt = data.get("id_olt")
    slot_numero = data.get("slot_numero")
    capacidad = data.get("capacidad_puertos_pon")


    # 🔍 Verificar existencia de OLT
    olt = OLT.query.get(id_olt)
    if not olt:
        abort(404, description="OLT no encontrada")

    # 🔒 Validar slot_numero dentro del rango permitido
    if not isinstance(slot_numero, int) or slot_numero < 0 or slot_numero >= olt.capacidad:
        abort(400, description=f"Slot inválido: debe estar entre 0 y {olt.capacidad - 1}")

    # 🚫 Validar que ese slot no esté ocupado
    if TarjetaOLT.query.filter_by(id_olt=id_olt, slot_numero=slot_numero).first():
        abort(400, description=f"El slot número {slot_numero} ya está ocupado en esta OLT")

    # ✅ Crear tarjeta OLT
    tarjeta = TarjetaOLT(**data)
    db.session.add(tarjeta)
    db.session.flush()  # Para obtener el ID antes de hacer commit
    
    if capacidad is None:
        abort(400, description="El campo 'capacidad_puertos_pon' es obligatorio.")
    # 🧠 Crear puertos PON según capacidad
    try:
        capacidad = int(capacidad)
        for i in range(capacidad):
            puerto = PuertoPONOLT(
                id_tarjeta_olt=tarjeta.id_tarjeta_olt,
                numero_puerto=i,
                estado_puerto=True
            )
            db.session.add(puerto)
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"Error al crear puertos: {str(e)}")

    # 🔄 Actualizar slots ocupados de la OLT
    olt.slots_ocupados = TarjetaOLT.query.filter_by(id_olt=id_olt).count()

    db.session.commit()
    return tarjeta



def actualizar_tarjeta_olt(id_tarjeta, data):
    tarjeta = TarjetaOLT.query.get(id_tarjeta)
    if not tarjeta:
        abort(404, description="Tarjeta OLT no encontrada")

    id_olt_nuevo = data.get("id_olt", tarjeta.id_olt)
    slot_nuevo = data.get("slot_numero", tarjeta.slot_numero)

    olt_nueva = OLT.query.get(id_olt_nuevo)
    if not olt_nueva:
        abort(404, description="OLT no encontrada")

    if not isinstance(slot_nuevo, int) or slot_nuevo < 0 or slot_nuevo >= olt_nueva.capacidad:
        abort(400, description=f"Slot inválido: debe estar entre 0 y {olt_nueva.capacidad - 1}")

    existente = TarjetaOLT.query.filter_by(id_olt=id_olt_nuevo, slot_numero=slot_nuevo).first()
    if existente and existente.id_tarjeta_olt != id_tarjeta:
        abort(400, description=f"El slot {slot_nuevo} ya está ocupado en esa OLT")

    # 👀 Verificar si cambia la capacidad de puertos
    nueva_capacidad = data.get("capacidad_puertos_pon", tarjeta.capacidad_puertos_pon)
    try:
        nueva_capacidad = int(nueva_capacidad)
    except Exception:
        abort(400, description="La capacidad de puertos debe ser un número entero válido.")

    capacidad_anterior = tarjeta.capacidad_puertos_pon
    tarjeta.capacidad_puertos_pon = nueva_capacidad

    # ✅ Actualizar otros campos
    tarjeta.id_olt = id_olt_nuevo
    tarjeta.slot_numero = slot_nuevo
    tarjeta.nombre = data.get("nombre", tarjeta.nombre)
    tarjeta.estado = data.get("estado", tarjeta.estado)

    # 🧠 Si la nueva capacidad es menor, eliminar puertos sobrantes
    if nueva_capacidad < capacidad_anterior:
        PuertoPONOLT.query.filter(
            PuertoPONOLT.id_tarjeta_olt == id_tarjeta,
            PuertoPONOLT.numero_puerto >= nueva_capacidad
        ).delete()

    # 🧠 Si la nueva capacidad es mayor, agregar puertos faltantes
    elif nueva_capacidad > capacidad_anterior:
        for i in range(capacidad_anterior, nueva_capacidad):
            nuevo_puerto = PuertoPONOLT(
                id_tarjeta_olt=id_tarjeta,
                numero_puerto=i,
                estado_puerto=True
            )
            db.session.add(nuevo_puerto)

    db.session.commit()

    # 🔄 Actualizar slots ocupados de la OLT (por si cambió)
    for olt_id in {tarjeta.id_olt, id_olt_nuevo}:
        olt = OLT.query.get(olt_id)
        if olt:
            olt.slots_ocupados = TarjetaOLT.query.filter_by(id_olt=olt.id_olt).count()
    db.session.commit()

    return tarjeta




def eliminar_tarjeta_olt(id_tarjeta):
    tarjeta = TarjetaOLT.query.get(id_tarjeta)
    if not tarjeta:
        abort(404, description="Tarjeta OLT no encontrada")

    id_olt = tarjeta.id_olt

    try:
        # 🔁 Eliminar puertos PON asociados
        PuertoPONOLT.query.filter_by(id_tarjeta_olt=id_tarjeta).delete()

        # ❌ Eliminar la tarjeta OLT
        db.session.delete(tarjeta)

        # 🔄 Actualizar los slots ocupados de la OLT
        olt = OLT.query.get(id_olt)
        if olt:
            olt.slots_ocupados = TarjetaOLT.query.filter_by(id_olt=id_olt).count()

        db.session.commit()
        return tarjeta

    except Exception as e:
        db.session.rollback()
        abort(500, description=f"Error al eliminar tarjeta y puertos: {str(e)}")
