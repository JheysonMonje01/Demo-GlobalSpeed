from flask import Blueprint, request, jsonify
from app.services.informacion_transferencia_service import (
    crear_informacion_transferencia,
    actualizar_informacion_transferencia,
    obtener_informacion_transferencia_por_id,
    obtener_informaciones_transferencia_filtradas,
    eliminar_informacion_transferencia
)
from app.schemas.informacion_metodo_pago_schema import InformacionMetodoPagoSchema

# Nombre del blueprint consistente
informacion_metodo_pago_bp = Blueprint("informacion_metodo_pago", __name__)
schema = InformacionMetodoPagoSchema()
schema_many = InformacionMetodoPagoSchema(many=True)

# POST - Crear información de transferencia
@informacion_metodo_pago_bp.route("/", methods=["POST"])
def post_transferencia():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Datos JSON requeridos"}), 400

    resultado, codigo = crear_informacion_transferencia(data)
    if isinstance(resultado, dict) and "error" in resultado:
        return jsonify(resultado), codigo

    return schema.jsonify(resultado), codigo

# PUT - Actualizar información de transferencia
@informacion_metodo_pago_bp.route("/<int:id_info>", methods=["PUT"])
def put_transferencia(id_info):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Datos JSON requeridos"}), 400

    resultado, codigo = actualizar_informacion_transferencia(id_info, data)
    if isinstance(resultado, dict) and "error" in resultado:
        return jsonify(resultado), codigo

    return schema.jsonify(resultado), codigo



@informacion_metodo_pago_bp.route("/", methods=["GET"])
def listar_informacion_transferencia():
    filtros = request.args.to_dict()
    resultado, codigo = obtener_informaciones_transferencia_filtradas(filtros)

    if isinstance(resultado, dict) and "error" in resultado:
        return jsonify(resultado), codigo

    return schema_many.jsonify(resultado), codigo


@informacion_metodo_pago_bp.route("/<int:id_info>", methods=["GET"])
def obtener_transferencia(id_info):
    resultado, codigo = obtener_informacion_transferencia_por_id(id_info)
    if isinstance(resultado, dict) and "error" in resultado:
        return jsonify(resultado), codigo

    return schema.jsonify(resultado), codigo


@informacion_metodo_pago_bp.route("/<int:id_info>", methods=["DELETE"])
def eliminar_transferencia(id_info):
    resultado, codigo = eliminar_informacion_transferencia(id_info)
    return jsonify(resultado), codigo
