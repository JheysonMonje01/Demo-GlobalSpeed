# app/routes/puerto_tarjeta_routes.py

from flask import Blueprint, request, jsonify
from app.schemas.puerto_pon_olt_schema import PuertoPONOLT_Schema
from app.services.puerto_pon_olt_service import (
    listar_puertos, obtener_puerto, crear_puerto,
    actualizar_puerto, eliminar_puerto
)
from sqlalchemy.exc import SQLAlchemyError

puerto_bp = Blueprint('puerto_bp', __name__)
puerto_schema = PuertoPONOLT_Schema()
puertos_schema = PuertoPONOLT_Schema(many=True)

@puerto_bp.route('/puertos', methods=['GET'])
def listar():
    try:
        id_tarjeta_olt = request.args.get("id_tarjeta_olt")
        if id_tarjeta_olt:
            puertos = listar_puertos(id_tarjeta_olt=int(id_tarjeta_olt))
        else:
            puertos = listar_puertos()
        return jsonify(puertos_schema.dump(puertos)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@puerto_bp.route('/puertos/tarjeta/<int:id_tarjeta_olt>', methods=['GET'])
def obtener_por_tarjeta(id_tarjeta_olt):
    try:
        puertos = listar_puertos(id_tarjeta_olt=id_tarjeta_olt)
        return jsonify(puertos_schema.dump(puertos)), 200
    except Exception as e:
        return jsonify({"error": f"Error al obtener puertos de la tarjeta: {str(e)}"}), 500


@puerto_bp.route('/puertos/<int:id_puerto>', methods=['GET'])
def obtener(id_puerto):
    puerto = obtener_puerto(id_puerto)
    if not puerto:
        return jsonify({"error": "Puerto no encontrado"}), 404
    return jsonify(puerto_schema.dump(puerto)), 200

@puerto_bp.route('/puertos', methods=['POST'])
def crear():
    data = request.get_json()
    try:
        puerto = crear_puerto(data)
        return jsonify(puerto_schema.dump(puerto)), 201
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@puerto_bp.route('/puertos/<int:id_puerto>', methods=['PUT'])
def actualizar(id_puerto):
    data = request.get_json()
    try:
        puerto = actualizar_puerto(id_puerto, data)
        return jsonify(puerto_schema.dump(puerto)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@puerto_bp.route('/puertos/<int:id_puerto>', methods=['DELETE'])
def eliminar(id_puerto):
    try:
        eliminar_puerto(id_puerto)
        return jsonify({"mensaje": "Puerto eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
