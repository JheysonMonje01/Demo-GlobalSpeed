from flask import Blueprint, request, jsonify
from app.services.orden_pago_service import crear_orden_inicial, verificar_vencimientos_ordenes, actualizar_orden_pago, obtener_ordenes_por_contrato, obtener_ordenes_por_estado, crear_orden_manual, obtener_todas_las_ordenes

orden_pago_bp = Blueprint("orden_pago", __name__)


"""ENDPOINT PARA CREAR LA ORDEN DE PAGO INICIAL AL CREAR UN CONTRATO"""
@orden_pago_bp.route("/crear", methods=["POST"])
def crear_ordenes_pago():
    data = request.get_json()

    id_contrato = data.get("id_contrato")
    id_plan = data.get("id_plan")
    fecha_inicio = data.get("fecha_inicio")

    if not all([id_contrato, id_plan, fecha_inicio]):
        return jsonify({
            "status": "error",
            "message": "❌ Faltan campos requeridos: id_contrato, id_plan, fecha_inicio"
        }), 400

    success, message, ordenes = crear_orden_inicial(id_contrato, id_plan, fecha_inicio)

    if success:
        return jsonify({
            "status": "success",
            "message": message,
            "ordenes": ordenes
        }), 201
    else:
        return jsonify({
            "status": "error",
            "message": message
        }), 500


"""ENDPOINT PARA VERIFICAR VENCIMIENTOS DE ORDENES"""

@orden_pago_bp.route("/verificar-vencimientos", methods=["PUT"])
def verificar_vencimientos():
    resultado = verificar_vencimientos_ordenes()
    status_code = 200 if resultado["status"] == "success" else 500
    return jsonify(resultado), status_code



"""ENDPOINT PARA OBTENER ESTADO DE ORDENES DE PAGO"""

@orden_pago_bp.route("/<int:id_orden_pago>", methods=["PUT"])
def put_orden_pago(id_orden_pago):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Datos JSON requeridos."}), 400

    respuesta, status = actualizar_orden_pago(id_orden_pago, data)
    return jsonify(respuesta), status


"""ENDPOINT PARA LISTAR EL HISTORIA DE ORDENES DE PAGO"""

@orden_pago_bp.route("/contrato/<int:id_contrato>", methods=["GET"])
def get_ordenes_por_contrato(id_contrato):
    estado = request.args.get("estado")  # opcional: "pendiente", "vencido", "cancelado"

    datos, status = obtener_ordenes_por_contrato(id_contrato, estado)
    return jsonify(datos), status


@orden_pago_bp.route("/estado/<string:estado>", methods=["GET"])
def listar_ordenes_por_estado(estado):
    resultado, codigo = obtener_ordenes_por_estado(estado)
    return jsonify(resultado), codigo


"""ENDPOINT PARA CREAR LA ORDEN DE PAGO MANUALMENTE"""


@orden_pago_bp.route("/crear_manual", methods=["POST"])
def crear_orden_manual_route():
    data = request.get_json()
    resultado, codigo = crear_orden_manual(data)
    return jsonify(resultado), codigo

#obtener todas las ordenes
@orden_pago_bp.route("", methods=["GET"])
def listar_todas_las_ordenes():
    resultado, codigo = obtener_todas_las_ordenes()
    return jsonify(resultado), codigo

from app.services.orden_pago_service import obtener_ordenes_con_detalle, obtener_ordenes_por_contrato_estados_con_detalle

@orden_pago_bp.route("/con-detalle", methods=["GET"])
def listar_ordenes_con_detalle():
    datos, status = obtener_ordenes_con_detalle()
    return jsonify(datos), status

@orden_pago_bp.route('/detalle/contrato/<int:id_contrato>', methods=['GET'])
def ordenes_con_detalle_por_contrato(id_contrato):
    return obtener_ordenes_por_contrato_estados_con_detalle(id_contrato)

