from flask import Blueprint, request, jsonify
from app.services.pppoe_service import crear_usuario_pppoe, actualizar_usuario_pppoe, obtener_usuarios_pppoe, eliminar_usuario_pppoe
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
pppoe_bp = Blueprint('pppoe_bp', __name__)
import time

@pppoe_bp.route('/crear', methods=['POST'])
def crear_pppoe():
    try:
        start_time = time.perf_counter()
        data = request.get_json()
        logger.info("📥 [POST /crear] Datos recibidos: %s", data)

        resultado = crear_usuario_pppoe(data)
        logger.info("✅ Usuario PPPoE creado correctamente")
        end_time = time.perf_counter()
        tiempo_espera = end_time - start_time
        logging.info(f"🕒 Tiempo de espera crear_contrato: {tiempo_espera:.3f} segundos")
        
        return resultado
    except Exception as e:
        logger.error("❌ Error en [POST /crear]: %s", str(e), exc_info=True)
        return jsonify({"message": f"Error al crear usuario PPPoE: {str(e)}"}), 500


"""ENDPONINT PARA CREAR UN USUARIO DINAMICO PPPoE NUEVO"""
from app.services.pppoe_service import crear_usuario_pppoe_automatico

@pppoe_bp.route('/crear-automatico', methods=['POST'])
def crear_pppoe_automatico():
    try:
        start_time = time.perf_counter()
        data = request.get_json()
        logger.info("📥 [POST /crear-automatico] Datos recibidos: %s", data)

        resultado, codigo = crear_usuario_pppoe_automatico(data)
        end_time = time.perf_counter()
        logger.info("✅ Resultado creación automática: %s", resultado)
        tiempo_espera = end_time - start_time
        logging.info(f"🕒 Tiempo de espera crear_pppoe: {tiempo_espera:.3f} segundos")

        return jsonify(resultado), codigo
    except Exception as e:
        logger.error("❌ Error en [POST /crear-automatico]: %s", str(e), exc_info=True)
        return jsonify({"message": f"Error al crear usuario automático: {str(e)}"}), 500


"""ENNDPOINT PARA ACTUALIZAR UN USUARIO PPPoE EXISTENTE"""

@pppoe_bp.route('/<int:id_usuario>', methods=['PUT'])
def put_usuario_pppoe(id_usuario):
    data = request.get_json()
    resultado, codigo = actualizar_usuario_pppoe(id_usuario, data)
    return jsonify(resultado), codigo


"""ENDPOINT PARA OBTENER TODOS LOS USUARIOS PPPoE"""


@pppoe_bp.route('/', methods=['GET'])
def get_usuarios_pppoe():
    filtros = request.args.to_dict()
    resultado, codigo = obtener_usuarios_pppoe(filtros)
    return jsonify(resultado), codigo


""" ENDPOINT PARA ELIMINAR UN USUARIO PPPoE """

@pppoe_bp.route('/<int:id_usuario_pppoe>', methods=['DELETE'])
def delete_usuario_pppoe(id_usuario_pppoe):
    resultado, codigo = eliminar_usuario_pppoe(id_usuario_pppoe)
    return jsonify(resultado), codigo

""" Listar PPPoE """

from app.services.pppoe_service import obtener_detalle_pppoe,obtener_pppoe_por_id
@pppoe_bp.route('/detalle', methods=['GET'])
def listar_detalle_pppoe():
    return obtener_detalle_pppoe()

"""OBTENER PPPOE CON ID"""
@pppoe_bp.route('/<int:id_usuario_pppoe>', methods=['GET'])
def get_pppoe_por_id(id_usuario_pppoe):
    try:
        usuario = obtener_pppoe_por_id(id_usuario_pppoe)
        if usuario:
            return jsonify({'status': 'success', 'data': usuario}), 200
        return jsonify({'status': 'error', 'message': 'Usuario PPPoE no encontrado'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500