# routes/plan_routes.py
from flask import Blueprint, request, jsonify
from app.services.plan_service import crear_plan, obtener_plan_por_id, buscar_planes, eliminar_plan
from app.models.plan_model import PlanInternet
from flask_cors import CORS

from app.schemas.plan_schema import PlanSchema

plan_bp = Blueprint('plan_bp', __name__)
CORS(plan_bp) 
plan_schema = PlanSchema()
planes_schema = PlanSchema(many=True)

@plan_bp.route('/crear_plan', methods=['POST'])
def crear():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "Datos no proporcionados"}), 400

    exito, resultado = crear_plan(data)

    if exito:
        return jsonify(plan_schema.dump(resultado)), 201
    else:
        return jsonify({"status": "error", "message": resultado}), 400


"""****************************************************************************"""

plan_schema = PlanSchema()

@plan_bp.route('/<int:id_plan>', methods=['GET'])
def obtener_plan(id_plan):
    exito, resultado = obtener_plan_por_id(id_plan)

    if exito:
        return jsonify(plan_schema.dump(resultado)), 200
    else:
        return jsonify({"status": "error", "message": resultado}), 404



"""ENDPOINT PARA ACTUALIZAR UN PLAN DE INTERNET"""

@plan_bp.route('/actualizar/<int:id_plan>', methods=['PUT'])
def actualizar(id_plan):
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"status": "error", "message": "Formato JSON inválido o no proporcionado"}), 400

    if not data:
        return jsonify({"status": "error", "message": "Datos no proporcionados"}), 400

    from app.services.plan_service import actualizar_plan
    exito, resultado = actualizar_plan(id_plan, data)

    if exito:
        return jsonify(plan_schema.dump(resultado)), 200
    else:
        print("❌ Error en actualizar_plan:", resultado)  # 👈 Log importante
        return jsonify({"status": "error", "message": resultado}), 400




"""ENDPOINT PARA BUSCAR PLANES DE INTERNET CON FILTROS"""

from flask import Blueprint, request, jsonify
from app.services.plan_service import buscar_planes

@plan_bp.route("/buscar", methods=["GET"])
def get_planes():
    try:
        filtros_permitidos = [
            "id_plan",
            "nombre_plan",
            "velocidad_subida",
            "velocidad_bajada",
            "precio",
            "id_vlan"
        ]
        filtros = {}

        for key in request.args:
            if key in filtros_permitidos:
                filtros[key] = request.args.get(key)
            else:
                return jsonify({
                    "status": "error",
                    "message": f"Filtro no permitido: {key}"
                }), 400

        if not filtros:
            return jsonify({
                "status": "error",
                "message": "Debe proporcionar al menos un filtro de búsqueda válido."
            }), 400

        exito, resultado = buscar_planes(filtros)

        if not exito:
            return jsonify({"status": "error", "message": resultado}), 404

        if isinstance(resultado, list):
            return jsonify({"status": "success", "data": planes_schema.dump(resultado)}), 200
        else:
            return jsonify({"status": "success", "data": plan_schema.dump(resultado)}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error inesperado: {str(e)}"}), 500


@plan_bp.route("/", methods=["GET"])
def listar_todos():
    from app.services.plan_service import listar_todos_los_planes
    exito, resultado = listar_todos_los_planes()

    if exito:
        return jsonify({"status": "success", "data": resultado}), 200
    else:
        return jsonify({"status": "error", "message": resultado}), 500



"""ENDPOINT PARA ELIMINAR UN PLAN DE INTERNET"""

@plan_bp.route('/<int:id_plan>', methods=['DELETE'])
def eliminar(id_plan):
    try:
        exito, mensaje = eliminar_plan(id_plan)

        if exito:
            return jsonify({
                "status": "success",
                "message": mensaje
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": mensaje
            }), 400

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error inesperado al eliminar el plan: {str(e)}"
        }), 500


