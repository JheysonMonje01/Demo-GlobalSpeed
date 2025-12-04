from flask import Blueprint, request, jsonify, abort
from app.services.tarjeta_olt_service import (
    crear_tarjeta_olt,
    listar_tarjetas_olt,
    obtener_tarjeta_olt,
    actualizar_tarjeta_olt,
    eliminar_tarjeta_olt
)
from app.schemas.tarjeta_olt_schema import TarjetaOLTSchema
from werkzeug.exceptions import BadRequest

tarjeta_olt_bp = Blueprint('tarjeta_olt_bp', __name__)
tarjeta_schema = TarjetaOLTSchema()
tarjetas_schema = TarjetaOLTSchema(many=True)

# Crear tarjeta OLT
@tarjeta_olt_bp.route('/tarjetas-olt', methods=['POST'])
def crear():
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("El cuerpo de la solicitud está vacío o mal formado.")
        nueva_tarjeta = crear_tarjeta_olt(data)
        return jsonify(tarjeta_schema.dump(nueva_tarjeta)), 201
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400

# Listar todas las tarjetas
@tarjeta_olt_bp.route('/tarjetas-olt', methods=['GET'])
def listar():
    tarjetas = listar_tarjetas_olt()
    return jsonify(tarjetas_schema.dump(tarjetas)), 200

# Obtener tarjeta por ID
@tarjeta_olt_bp.route('/tarjetas-olt/<int:id_tarjeta>', methods=['GET'])
def obtener_por_id(id_tarjeta):
    tarjeta = obtener_tarjeta_olt(id_tarjeta)
    if not tarjeta:
        abort(404, description=f"La tarjeta OLT con ID {id_tarjeta} no existe.")
    return jsonify(tarjeta_schema.dump(tarjeta)), 200

# Actualizar tarjeta OLT
@tarjeta_olt_bp.route('/tarjetas-olt/<int:id_tarjeta>', methods=['PUT'])
def actualizar(id_tarjeta):
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("El cuerpo de la solicitud está vacío o mal formado.")
        tarjeta_actualizada = actualizar_tarjeta_olt(id_tarjeta, data)
        return jsonify(tarjeta_schema.dump(tarjeta_actualizada)), 200
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        abort(404, description=f"No se pudo actualizar. La tarjeta OLT con ID {id_tarjeta} no existe.")

# Eliminar tarjeta
@tarjeta_olt_bp.route('/tarjetas-olt/<int:id_tarjeta>', methods=['DELETE'])
def eliminar(id_tarjeta):
    tarjeta = obtener_tarjeta_olt(id_tarjeta)
    if not tarjeta:
        abort(404, description=f"No se pudo eliminar. La tarjeta OLT con ID {id_tarjeta} no existe.")
    eliminar_tarjeta_olt(id_tarjeta)
    return jsonify({'mensaje': f'Tarjeta OLT con ID {id_tarjeta} eliminada correctamente'}), 200
