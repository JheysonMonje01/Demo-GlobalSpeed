from flask import Blueprint, request, jsonify
from app.services.pago_service import (
    crear_pago,
    actualizar_pago,
    obtener_pago_por_id,
    listar_pagos_con_filtros,
    eliminar_pago,
    obtener_pagos_por_contrato,
    obtener_pagos_con_detalle
)
from app.services.pago_transferencia_service import (
    registrar_pago_transferencia,
    actualizar_comprobante_pago
)
from app.schemas.pago_schema import PagoSchema

pago_bp = Blueprint("pago_bp", __name__)
pago_schema = PagoSchema()
pago_list_schema = PagoSchema(many=True)

# POST /pagos (Pago físico)
@pago_bp.route("/crear_pago_fisico", methods=["POST"])
def crear_pago_route():
    data = request.get_json()
    resultado, codigo = crear_pago(data)
    if codigo in [200, 201]:
        return pago_schema.jsonify(resultado), codigo
    return jsonify(resultado), codigo

# POST /pagos/transferencia (Pago transferencia con archivo)
@pago_bp.route("/crear_pago_transferencia", methods=["POST"])
def crear_pago_transferencia_route():
    if 'file' not in request.files:
        return jsonify({"error": "Debe adjuntar el archivo con el campo 'file'."}), 400

    file = request.files['file']
    data = request.form.to_dict()

    resultado, codigo = registrar_pago_transferencia(data, file)
    if codigo in [200, 201]:
        return pago_schema.jsonify(resultado), codigo
    return jsonify(resultado), codigo

# PUT /pagos/<id_pago> (Actualizar datos generales)
@pago_bp.route("/actualizar_pago_fisico/<int:id_pago>", methods=["PUT"])
def actualizar_pago_route(id_pago):
    data = request.get_json()
    resultado, codigo = actualizar_pago(id_pago, data)
    if codigo == 200:
        return pago_schema.jsonify(resultado), 200
    return jsonify(resultado), codigo

# PUT /pagos/<id_pago>/comprobante (Actualizar comprobante de transferencia)
@pago_bp.route("/actualizar_comprobante/<int:id_pago>", methods=["PUT"])
def actualizar_comprobante_route(id_pago):
    if 'file' not in request.files:
        return jsonify({"error": "Debe adjuntar un comprobante en el campo 'file'."}), 400

    file = request.files['file']
    resultado, codigo = actualizar_comprobante_pago(id_pago, file)
    if codigo == 200:
        return pago_schema.jsonify(resultado), 200
    return jsonify(resultado), codigo

# GET /pagos/<id_pago>
@pago_bp.route("/<int:id_pago>", methods=["GET"])
def obtener_pago_por_id_route(id_pago):
    resultado, codigo = obtener_pago_por_id(id_pago)
    if codigo == 200:
        return pago_schema.jsonify(resultado), 200
    return jsonify(resultado), codigo

# GET /pagos (Con filtros: id_contrato, id_metodo_pago, estado, desde, hasta, mes)
@pago_bp.route("/", methods=["GET"])
def listar_pagos_con_filtros_route():
    filtros = request.args.to_dict()
    resultado, codigo = listar_pagos_con_filtros(filtros)
    if codigo == 200:
        return pago_list_schema.jsonify(resultado), 200
    return jsonify(resultado), codigo

# DELETE /pagos/eliminar_pago/<id_pago>
@pago_bp.route("/eliminar_pago/<int:id_pago>", methods=["DELETE"])
def eliminar_pago_route(id_pago):
    resultado, codigo = eliminar_pago(id_pago)
    return jsonify(resultado), codigo

@pago_bp.route("/contrato/<int:id_contrato>", methods=["GET"])
def listar_pagos_por_contrato(id_contrato):
    try:
        pagos = obtener_pagos_por_contrato(id_contrato)
        return jsonify(pagos), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pago_bp.route('/detallado', methods=['GET'])
def listar_pagos_detallado():
    try:
        resultado = obtener_pagos_con_detalle()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500