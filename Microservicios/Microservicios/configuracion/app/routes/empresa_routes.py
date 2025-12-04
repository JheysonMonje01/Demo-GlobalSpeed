from flask import Blueprint, request, jsonify
from app.schemas.empresa_schema import EmpresaSchema, EmpresaTelefonoSchema, EmpresaCorreoSchema
from app.services.empresa_service import (
    crear_empresa,
    actualizar_empresa,
    obtener_empresas_filtradas,
    agregar_telefono,
    agregar_correo,
    actualizar_empresa_json
)
from app.extensions import db

empresa_bp = Blueprint('empresa_bp', __name__)
empresa_schema = EmpresaSchema(context={"session": db.session})
empresas_schema = EmpresaSchema(many=True)
telefono_schema = EmpresaTelefonoSchema()
correo_schema = EmpresaCorreoSchema()

"""****************************************************************************"""
""" CREAR EMPRESA """
from flask import request
import json
from app.models.empresa_model import Empresa, EmpresaTelefono, EmpresaCorreo

@empresa_bp.route('/empresa', methods=['POST'])
def post_empresa():
    try:
        result = crear_empresa(request.form, request.files)

        if result['status'] == 'success':
            return jsonify(empresa_schema.dump(result['data'])), 201
        else:
            return jsonify({'error': result['message']}), 400

    except Exception as e:
        return jsonify({'error': f"Error al crear empresa: {str(e)}"}), 500

"""****************************************************************************"""
""" ACTUALIZAR EMPRESA """
@empresa_bp.route('/empresa/<int:id_empresa>', methods=['PUT'])
def put_empresa(id_empresa):
    try:
        if request.is_json:
            # 🧾 JSON puro
            form_data = request.get_json()
            result = actualizar_empresa_json(id_empresa, form_data)
        else:
            # 📦 Form-data (con archivos y texto plano)
            result = actualizar_empresa(id_empresa, request.form, request.files)

        if result['status'] == 'success':
            return jsonify(empresa_schema.dump(result['data'])), 200
        else:
            return jsonify({'error': result['message']}), 400

    except Exception as e:
        return jsonify({'error': f"Error al actualizar empresa: {str(e)}"}), 500

"""****************************************************************************"""
""" LISTAR EMPRESAS """
@empresa_bp.route('/empresa', methods=['GET'])
def listar_empresas():
    try:
        filtros = request.args.to_dict()
        empresas = obtener_empresas_filtradas(filtros)
        return jsonify(empresas_schema.dump(empresas))
    except Exception as e:
        return jsonify({"error": f"Error al obtener empresas: {str(e)}"}), 500


"""****************************************************************************"""
""" AGREGAR TELÉFONO """
@empresa_bp.route('/empresa/<int:id_empresa>/telefonos', methods=['POST'])
def post_telefono(id_empresa):
    data = request.get_json()
    result = agregar_telefono(id_empresa, data)

    if result['status'] == 'success':
        return jsonify(telefono_schema.dump(result['data'])), 201
    return jsonify({"error": result["message"]}), 400


"""****************************************************************************"""
""" AGREGAR CORREO """
@empresa_bp.route('/empresa/<int:id_empresa>/correos', methods=['POST'])
def post_correo(id_empresa):
    data = request.get_json()
    result = agregar_correo(id_empresa, data)

    if result['status'] == 'success':
        return jsonify(correo_schema.dump(result['data'])), 201
    return jsonify({"error": result["message"]}), 400
