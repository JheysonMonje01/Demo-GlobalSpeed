from flask import Blueprint, request, jsonify
from app.services.ip_pool_service import crear_ip_pool, obtener_pool_por_id, obtener_ip_pools, listar_todos_los_pools
from app.schemas.ip_pool_schema import IpPoolSchema
from marshmallow import ValidationError
from app.extensions import db
import logging
import re


ip_pool_bp = Blueprint("ip_pool_bp", __name__)
schema = IpPoolSchema()

# POST /pools → Crear pool IP
@ip_pool_bp.route("/ip_pools", methods=["POST"])
def crear():
    try:
        data = request.get_json()
        # Validación con Marshmallow
        validado = schema.load(data, session=db.session)

        exito, mensaje = crear_ip_pool(validado)
        if exito:
            return jsonify({"status": "success", "message": mensaje}), 201
        else:
            return jsonify({"status": "error", "message": mensaje}), 400

    except ValidationError as e:
        return jsonify({"status": "error", "message": "Datos inválidos", "errors": e.messages}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error inesperado: {str(e)}"}), 500


"""ENDPOINT PARA OBTENER TODOS LOS POOLS IP"""

@ip_pool_bp.route("/<int:id_pool>", methods=["GET"])
def obtener_pool(id_pool):
    try:
        exito, resultado = obtener_pool_por_id(id_pool)
        if not exito:
            return jsonify({"status": "error", "message": resultado}), 404

        return jsonify(schema.dump(resultado)), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error inesperado: {str(e)}"
        }), 500


@ip_pool_bp.route("", methods=["GET"])
def listar_pools():
    exito, resultado = obtener_ip_pools()
    if exito:
        schema_many = IpPoolSchema(many=True, context={"session": db.session})
        print("[DEBUG] Resultado obtenido desde DB:", resultado)
        return jsonify(schema_many.dump(resultado)), 200
    else:
        return jsonify({"status": "error", "message": resultado}), 500

"""******************************************************************************************"""


"""ENDPOINT PARA LISTAR TODOS LOS POOLS PARA EL MICROSERVICIO DE GESTION SERVICIO"""

@ip_pool_bp.route("/todos", methods=["GET"])
def listar_pools_todos():
    try:
        exito, resultado = listar_todos_los_pools()
        if not exito:
            return jsonify({
                "status": "error",
                "message": "No se pudo listar pools",
                "detalle": resultado
            }), 500

        # Serializar con many=True
        return jsonify(IpPoolSchema(many=True).dump(resultado)), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error inesperado: {str(e)}"
        }), 500


"""ENDPOINT PARA OBTENER UN POOL POR NOMBRE PARA EL MICROSERVICIO DE GESTION SERVICIO"""

@ip_pool_bp.route("/nombre/<string:nombre_pool>", methods=["GET"])
def obtener_pool_por_nombre(nombre_pool):
    try:
        from app.models.ip_pool_model import IpPool
        pool = IpPool.query.filter_by(nombre=nombre_pool).first()

        if not pool:
            return jsonify({"status": "error", "message": f"No se encontró un pool con el nombre '{nombre_pool}'"}), 404

        schema = IpPoolSchema()
        return jsonify({"status": "success", "pool": schema.dump(pool)}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error inesperado: {str(e)}"}), 500
