from app.models.olt import OLT
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from flask import abort
from app.utils.contraseña_gestion import hash_password

def crear_olt(data):
    try:
        # Validaciones de campos obligatorios
        campos_obligatorios = ['id_datacenter', 'marca', 'modelo', 'capacidad', 'ip_gestion', 'usuario_gestion', 'contrasena_gestion']
        for campo in campos_obligatorios:
            if campo not in data or not data[campo]:
                abort(400, description=f"El campo '{campo}' es obligatorio.")

        # Validación de capacidad
        if not isinstance(data['capacidad'], int) or data['capacidad'] <= 0:
            abort(400, description="La capacidad debe ser un número entero positivo.")

        # Validación de IP de gestión (sencilla)
        if len(data['ip_gestion'].split(".")) != 4:
            abort(400, description="IP de gestión inválida.")

        # Encriptar la contraseña antes de guardar
        data['contrasena_gestion'] = hash_password(data['contrasena_gestion'])

        nueva_olt = OLT(**data)
        db.session.add(nueva_olt)
        db.session.commit()
        return nueva_olt

    except SQLAlchemyError as e:
        db.session.rollback()
        abort(500, description=f"Error al crear OLT: {str(e)}")


def obtener_olts_filtradas(filtros):
    try:
        query = OLT.query
        filtros_permitidos = {'marca', 'modelo', 'id_datacenter'}

        for key, value in filtros.items():
            if key not in filtros_permitidos:
                raise ValueError(f"Filtro no válido: {key}")
            if key == 'id_datacenter':
                query = query.filter(OLT.id_datacenter == value)
            elif key == 'marca':
                query = query.filter(OLT.marca.ilike(f"%{value}%"))
            elif key == 'modelo':
                query = query.filter(OLT.modelo.ilike(f"%{value}%"))

        return query.all()
    except ValueError as ve:
        abort(400, description=str(ve))
    except Exception as e:
        abort(500, description="Error al obtener las OLTs.")


def obtener_olt_por_id(id_olt):
    olt = OLT.query.get(id_olt)
    if not olt:
        abort(404, description="OLT no encontrada")
    return olt


def actualizar_olt(id_olt, data):
    olt = obtener_olt_por_id(id_olt)
    try:
        # Evitar actualizar campos no permitidos como id_olt
        campos_actualizables = ['marca', 'modelo', 'capacidad', 'ip_gestion', 'usuario_gestion', 'contrasena_gestion', 'estado']

        for key, value in data.items():
            if key not in campos_actualizables:
                continue
            if key == 'contrasena_gestion':
                value = hash_password(value)
            setattr(olt, key, value)

        db.session.commit()
        return olt
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(500, description=f"Error al actualizar OLT: {str(e)}")


def eliminar_olt(id_olt):
    olt = obtener_olt_por_id(id_olt)
    try:
        db.session.delete(olt)
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(500, description=f"Error al eliminar OLT: {str(e)}")
