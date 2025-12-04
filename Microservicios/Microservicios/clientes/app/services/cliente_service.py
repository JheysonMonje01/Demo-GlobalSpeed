from flask import jsonify
from app.db import db
from app.models.cliente_model import Cliente
from app.schemas.cliente_schema import cliente_schema, clientes_schema

def crear_cliente(data):
    errors = cliente_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    cliente = Cliente(**data)
    db.session.add(cliente)
    db.session.commit()
    return cliente_schema.jsonify(cliente), 201

# cliente_service.py
from app.schemas.cliente_schema import ClienteSchema

cliente_schema = ClienteSchema()              # Para un solo cliente
clientes_schema = ClienteSchema(many=True)    # Para lista de clientes

def listar_clientes():
    clientes = Cliente.query.all()
    return jsonify(clientes_schema.dump(clientes)), 200




def obtener_cliente(id_cliente):
    cliente = Cliente.query.get(id_cliente)
    if not cliente:
        return jsonify({"error": "Cliente no encontrado"}), 404
    return jsonify(cliente_schema.dump(cliente)), 200





from flask import jsonify
from app.db import db
from app.models.persona_model import Persona
from datetime import datetime

def sincronizar_datos_usuario(id_usuario, nuevo_correo=None, nuevo_telefono=None):
    """
    Sincroniza correo y/o teléfono del usuario con su registro en la tabla persona.

    Args:
        id_usuario (int): ID del usuario cuyo registro fue actualizado.
        nuevo_correo (str): Correo actualizado (opcional).
        nuevo_telefono (str): Teléfono actualizado (opcional).
    """
    persona = Persona.query.filter_by(id_usuario=id_usuario).first()

    if not persona:
        return jsonify({"error": "No existe una persona asociada a este usuario"}), 404

    actualizado = False

    if nuevo_correo and persona.correo != nuevo_correo:
        persona.correo = nuevo_correo
        actualizado = True

    if nuevo_telefono and persona.telefono != nuevo_telefono:
        persona.telefono = nuevo_telefono
        actualizado = True

    if actualizado:
        persona.fecha_modificacion = datetime.utcnow()
        db.session.commit()

    return jsonify({"mensaje": "Datos sincronizados correctamente"}), 200

from app.models.cliente_model import Cliente
from app.schemas.cliente_schema import cliente_schema
from flask import jsonify

def obtener_cliente_por_persona_service(id_persona):
    cliente = Cliente.query.filter_by(id_persona=id_persona).first()
    if not cliente:
        return jsonify({"error": "Cliente no encontrado para esta persona."}), 404
    return cliente_schema.dump(cliente), 200
