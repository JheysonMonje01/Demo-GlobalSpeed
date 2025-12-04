from flask import jsonify, request
from app import db
from app.models.rol_model import Rol

def crear_rol(data):
    nombre_rol = data.get("nombre_rol")
    descripcion = data.get("descripcion")

    if not nombre_rol:
        return jsonify({"error": "El nombre del rol es obligatorio"}), 400

    if Rol.query.filter_by(nombre_rol=nombre_rol).first():
        return jsonify({"error": "Ya existe un rol con ese nombre"}), 400

    nuevo_rol = Rol(nombre_rol=nombre_rol, descripcion=descripcion)
    db.session.add(nuevo_rol)
    db.session.commit()

    return jsonify({"mensaje": "Rol creado exitosamente"}), 201


"""FUNCIONES DE BUSQUEDAS DE ROLES"""

from sqlalchemy import asc

def buscar_roles():
    nombre = request.args.get('nombre')
    estado = request.args.get('estado')
    id_rol = request.args.get('id_rol')

    query = Rol.query

    if id_rol:
        query = query.filter(Rol.id_rol == id_rol)
    if nombre:
        query = query.filter(Rol.nombre_rol.ilike(f"%{nombre}%"))
    if estado is not None:
        if estado.lower() == 'true':
            query = query.filter(Rol.estado.is_(True))
        elif estado.lower() == 'false':
            query = query.filter(Rol.estado.is_(False))

    # Ordenamiento automático por id_rol ascendente
    query = query.order_by(asc(Rol.id_rol))

    roles = query.all()
    resultados = [
        {
            "id_rol": r.id_rol,
            "nombre_rol": r.nombre_rol,
            "descripcion": r.descripcion,
            "estado": r.estado,
            "fecha_creacion": r.fecha_creacion,
            "fecha_modificacion": r.fecha_modificacion,
        }
        for r in roles
    ]
    return jsonify(resultados), 200
