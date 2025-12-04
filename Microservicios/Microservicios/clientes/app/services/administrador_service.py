from flask import jsonify
from app.db import db
from app.models.administrador_model import Administrador
from app.schemas.administrador_schema import administrador_schema, administradores_schema

def crear_administrador(data):
    errors = administrador_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    administrador = Administrador(**data)
    db.session.add(administrador)
    db.session.commit()
    return administrador_schema.jsonify(administrador), 201

def listar_administradores():
    administradores = Administrador.query.all()
    return administradores_schema.jsonify(administradores), 200


def obtener_administrador(id_cliente):
    Administrador = Administrador.query.get(id_cliente)
    if not Administrador:
        return jsonify({"error": "Cliente no encontrado"}), 404
    return administrador_schema.jsonify(Administrador), 200
