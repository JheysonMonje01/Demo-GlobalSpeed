from flask import Blueprint, request, jsonify
from app.schemas.gestion_servicio_schema import GestionServicioSchema
from app.services.gestion_service import (
    registrar_evento_gestion,
    listar_todas_las_gestiones,
    obtener_gestiones_filtradas, activar_usuario_pppoe, desactivar_usuario_pppoe
)

gestion_bp = Blueprint("gestion_bp", __name__)
gestion_schema = GestionServicioSchema()
gestiones_schema = GestionServicioSchema(many=True)

# 👉 Registrar un nuevo evento de gestión (por ejemplo, al crear usuario PPPoE)
@gestion_bp.route("/registrar", methods=["POST"])
def registrar_gestion():
    try:
        data = request.get_json()
        nueva_gestion = registrar_evento_gestion(data)
        return jsonify(gestion_schema.dump(nueva_gestion)), 201
    except Exception as e:
        return jsonify({"error": f"Error al registrar gestión: {str(e)}"}), 500

# 👉 Listar todos los registros de gestión (sin filtros)
@gestion_bp.route("/todos", methods=["GET"])
def listar_gestiones():
    try:
        gestiones = listar_todas_las_gestiones()
        return jsonify(gestiones_schema.dump(gestiones)), 200
    except Exception as e:
        return jsonify({"error": f"Error al listar gestiones: {str(e)}"}), 500

# 👉 Filtros múltiples con query params
# Ejemplo: /gestion/filtrar?id_contrato=1&estado_servicio=0
@gestion_bp.route("/filtrar", methods=["GET"])
def filtrar_gestiones():
    try:
        filtros = request.args.to_dict()
        gestiones = obtener_gestiones_filtradas(filtros)
        return jsonify(gestiones_schema.dump(gestiones)), 200
    except Exception as e:
        return jsonify({"error": f"Error al filtrar gestiones: {str(e)}"}), 500

@gestion_bp.route('/pppoe/activar/<int:id_usuario_pppoe>', methods=['PUT'])
def endpoint_activar_pppoe(id_usuario_pppoe):
    data = request.get_json()
    id_usuario_admin = data.get("id_usuario")

    if not id_usuario_admin:
        return jsonify({"status": "error", "message": "Falta el ID del administrador"}), 400

    resultado, codigo = activar_usuario_pppoe(id_usuario_pppoe, id_usuario_admin)
    return jsonify(resultado), codigo

@gestion_bp.route('/pppoe/desactivar/<int:id_usuario_pppoe>', methods=['PUT'])
def endpoint_desactivar_pppoe(id_usuario_pppoe):
    data = request.get_json()
    id_usuario_admin = data.get("id_usuario")

    if not id_usuario_admin:
        return jsonify({"status": "error", "message": "Falta el ID del administrador"}), 400

    resultado, codigo = desactivar_usuario_pppoe(id_usuario_pppoe, id_usuario_admin)
    return jsonify(resultado), codigo

from app.services.monitoreo_service import obtener_trafico_usuario_pppoe_por_id

@gestion_bp.route("/pppoe/trafico/<int:id_usuario_pppoe>", methods=["GET"])
def consultar_trafico_pppoe(id_usuario_pppoe):
    result, status = obtener_trafico_usuario_pppoe_por_id(id_usuario_pppoe)
    return jsonify(result), status