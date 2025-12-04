from flask import jsonify, request
from app.db import db
from app.models.tecnico_model import Tecnico
from app.schemas.tecnico_schema import tecnico_schema, tecnicos_schema
from datetime import datetime

ESTADOS_VALIDOS = ['activo', 'ocupado', 'inactivo']

def crear_tecnico(data):
    errors = tecnico_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    
    # Validar estado (si se envía)
    estado = data.get('estado', 'activo')
    if estado not in ESTADOS_VALIDOS:
        return jsonify({"error": f"Estado inválido. Debe ser uno de: {ESTADOS_VALIDOS}"}), 400

    if 'estado' not in data:
        data['estado'] = 'activo'  # valor por defecto

    tecnico = Tecnico(**data)

    db.session.add(tecnico)
    db.session.commit()

    return jsonify(tecnico_schema.dump(tecnico)), 201


def listar_tecnicos():
    estado = request.args.get("estado")
    query = Tecnico.query

    if estado:
        if estado not in ESTADOS_VALIDOS:
            return jsonify({"error": f"Estado inválido. Debe ser uno de: {ESTADOS_VALIDOS}"}), 400
        query = query.filter_by(estado=estado)

    tecnicos = query.all()
    return jsonify(tecnicos_schema.dump(tecnicos)), 200


def obtener_tecnico(id_tecnico):
    tecnico = Tecnico.query.get(id_tecnico)
    if not tecnico:
        return jsonify({"error": "Técnico no encontrado"}), 404
    return jsonify(tecnico_schema.dump(tecnico)), 200


def actualizar_estado(id_tecnico, data):
    nuevo_estado = data.get("estado")

    if not nuevo_estado:
        return jsonify({"error": "El campo 'estado' es obligatorio."}), 400

    if nuevo_estado not in ESTADOS_VALIDOS:
        return jsonify({"error": f"Estado inválido. Debe ser uno de: {ESTADOS_VALIDOS}"}), 400

    tecnico = Tecnico.query.get(id_tecnico)
    if not tecnico:
        return jsonify({"error": "Técnico no encontrado."}), 404

    tecnico.estado = nuevo_estado
    tecnico.fecha_modificacion = datetime.utcnow()

    try:
        db.session.commit()
        return jsonify({"message": "Estado del técnico actualizado correctamente."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"No se pudo actualizar el estado: {str(e)}"}), 500

def obtener_tecnico_por_persona(id_persona):
    tecnico = Tecnico.query.filter_by(id_persona=id_persona).first()
    if not tecnico:
        return jsonify({"error": "Técnico no encontrado para el ID de persona dado."}), 404
    return jsonify(tecnico_schema.dump(tecnico)), 200
