from flask import Blueprint, request, jsonify
from app.schemas.configuracion_schema import ConfiguracionSchema
from app.services.configuracion_service import crear_configuracion, actualizar_configuracion
from app.extensions import db  # ✅ Se importa para pasar la sesión

config_bp = Blueprint('config_bp', __name__)

@config_bp.route('/configuracion', methods=['POST'])
def post_configuracion():
    data = request.get_json()
    schema = ConfiguracionSchema(context={"session": db.session})

    try:
        valid_data = schema.load(data)
        result = crear_configuracion(valid_data)

        if result['status'] == 'success':
            return jsonify(schema.dump(result['data'])), 201  # ✅ .dump + jsonify
        else:
            return jsonify({'error': result['message']}), 400

    except Exception as e:
        return jsonify({'error': f"Error de validación o servidor: {str(e)}"}), 500

"""*****************************************************************************"""
"""ENDPOINT PARA ACTUALIZAR DATOS DE UNA CONFIGURACIÓN"""

@config_bp.route('/configuracion/<int:id_configuracion>', methods=['PUT'])
def put_configuracion(id_configuracion):
    data = request.get_json()
    schema = ConfiguracionSchema(context={"session": db.session})

    try:
        valid_data = schema.load(data)
        result = actualizar_configuracion(id_configuracion, valid_data)

        if result['status'] == 'success':
            return jsonify(schema.dump(result['data'])), 200
        else:
            return jsonify({'error': result['message']}), 400

    except Exception as e:
        return jsonify({'error': f"Error al actualizar configuración: {str(e)}"}), 500


"""*****************************************************************************"""
"""ENDPOINT PARA OBTENER DATOS DE LA CONFIGURACIÓN FILTRADAS"""

from flask import Blueprint, request, jsonify
from app.schemas.configuracion_schema import ConfiguracionSchema
from app.services.configuracion_service import obtener_configuraciones_filtradas

config_schema = ConfiguracionSchema(many=True)

@config_bp.route('/configuracion', methods=['GET'])
def listar_configuraciones():
    try:
        filtros = request.args.to_dict()
        configuraciones = obtener_configuraciones_filtradas(filtros)
        return jsonify(config_schema.dump(configuraciones))
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Error al obtener configuraciones: {str(e)}"}), 500

