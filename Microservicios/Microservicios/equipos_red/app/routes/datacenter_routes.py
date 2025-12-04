from flask import Blueprint, request, jsonify
from app.schemas.datacenter_schema import DataCenterSchema
from app.services.datacenter_service import (
    crear_datacenter,
    actualizar_datacenter,
    obtener_datacenters_filtrados,
    obtener_datacenter,
    eliminar_datacenter
)
from app.extensions import db

datacenter_bp = Blueprint('datacenter_bp', __name__)
schema = DataCenterSchema(context={"session": db.session})
schema_many = DataCenterSchema(many=True)


# 🔹 Crear un nuevo DataCenter
@datacenter_bp.route('/datacenters', methods=['POST'])
def post_datacenter():
    data = request.get_json()
    try:
        valid_data = schema.load(data)
        result = crear_datacenter(valid_data)

        if result['status'] == 'success':
            return jsonify(schema.dump(result['data'])), 201
        else:
            return jsonify({'error': result['message']}), 400

    except Exception as e:
        return jsonify({'error': f"Error de validación o servidor: {str(e)}"}), 500


# 🔹 Actualizar un DataCenter existente
@datacenter_bp.route('/datacenters/<int:id_datacenter>', methods=['PUT'])
def put_datacenter(id_datacenter):
    data = request.get_json()
    try:
        valid_data = schema.load(data)
        result = actualizar_datacenter(id_datacenter, valid_data)

        if result['status'] == 'success':
            return jsonify(schema.dump(result['data'])), 200
        else:
            return jsonify({'error': result['message']}), 400

    except Exception as e:
        return jsonify({'error': f"Error al actualizar DataCenter: {str(e)}"}), 500


# 🔹 Obtener lista de DataCenters con filtros opcionales
@datacenter_bp.route('/datacenters', methods=['GET'])
def listar_datacenters():
    try:
        filtros = request.args.to_dict()
        datacenters = obtener_datacenters_filtrados(filtros)
        return jsonify(schema_many.dump(datacenters)), 200
    except Exception as e:
        return jsonify({'error': f"Error al obtener DataCenters: {str(e)}"}), 500


# 🔹 Obtener un DataCenter por ID
@datacenter_bp.route('/datacenters/<int:id_datacenter>', methods=['GET'])
def get_datacenter(id_datacenter):
    try:
        datacenter = obtener_datacenter(id_datacenter)
        return jsonify(schema.dump(datacenter)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404


# 🔹 Eliminar un DataCenter
@datacenter_bp.route('/datacenters/<int:id_datacenter>', methods=['DELETE'])
def delete_datacenter(id_datacenter):
    result = eliminar_datacenter(id_datacenter)

    if result['status'] == 'success':
        return jsonify({'message': result['message']}), 200
    else:
        return jsonify({'error': result['message']}), 400
