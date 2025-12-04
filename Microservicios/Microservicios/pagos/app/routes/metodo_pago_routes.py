from flask import Blueprint, request, jsonify
from app.schemas.metodo_pago_schema import MetodoPagoSchema
from app.services.metodo_pago_service import (
    crear_metodo_pago,
    actualizar_metodo_pago,
    obtener_metodo_pago_por_id,
    obtener_metodos_pago_filtrados,
    eliminar_metodo_pago
)

metodo_pago_bp = Blueprint('metodo_pago_bp', __name__)
schema = MetodoPagoSchema()

@metodo_pago_bp.route('', methods=['POST'])
def post_metodo_pago():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Datos JSON requeridos"}), 400

    errores = schema.validate(data)
    if errores:
        return jsonify({"error": errores}), 400

    resultado, codigo = crear_metodo_pago(data)
    if isinstance(resultado, dict) and "error" in resultado:
        return jsonify(resultado), codigo

    return schema.jsonify(resultado), codigo

@metodo_pago_bp.route('/<int:id>', methods=['PUT'])
def put_metodo_pago(id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Datos JSON requeridos"}), 400

    errores = schema.validate(data, partial=True)
    if errores:
        return jsonify({"error": errores}), 400

    resultado, codigo = actualizar_metodo_pago(id, data)
    if isinstance(resultado, dict) and "error" in resultado:
        return jsonify(resultado), codigo

    return schema.jsonify(resultado), codigo


"""*******************************************************************************"""


metodo_pago_schema = MetodoPagoSchema()
metodos_pago_schema = MetodoPagoSchema(many=True)


# GET por ID
@metodo_pago_bp.route("/<int:id_metodo>", methods=["GET"])
def get_metodo_pago(id_metodo):
    resultado, status = obtener_metodo_pago_por_id(id_metodo)
    if status != 200:
        return jsonify(resultado), status
    return metodo_pago_schema.jsonify(resultado), 200


# GET todos o con filtros
@metodo_pago_bp.route("/buscar", methods=["GET"])
def get_metodos_pago():
    filtros = request.args.to_dict()
    resultado, status = obtener_metodos_pago_filtrados(filtros)
    if status != 200:
        return jsonify(resultado), status
    return metodos_pago_schema.jsonify(resultado), 200


"""*******************************************************************************"""

@metodo_pago_bp.route("/borrar/<int:id_metodo_pago>", methods=["DELETE"])
def delete_metodo_pago(id_metodo_pago):
    resultado, codigo = eliminar_metodo_pago(id_metodo_pago)
    return jsonify(resultado), codigo


