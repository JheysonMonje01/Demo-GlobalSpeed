from flask import Blueprint, request
from app.services.cliente_service import crear_cliente, listar_clientes, sincronizar_datos_usuario

cliente_bp = Blueprint('cliente', __name__, url_prefix='/clientes')
import time
import logging
@cliente_bp.route('/', methods=['POST'])
def crear():
    data = request.get_json()
    start_time = time.perf_counter()
    end_time = time.perf_counter()
    tiempo_espera = end_time - start_time
    logging.info(f"🕒 Tiempo de espera crear_cliente: {tiempo_espera:.3f} segundos")
    return crear_cliente(data)


@cliente_bp.route('/sincronizar/<int:id_usuario>', methods=['PUT'])
def sincronizar_usuario(id_usuario):
    data = request.get_json()
    nuevo_correo = data.get("correo")
    nuevo_telefono = data.get("telefono")
    return sincronizar_datos_usuario(id_usuario, nuevo_correo, nuevo_telefono)

"""*******************************************************************"""

from flask import Blueprint, request
from app.services.cliente_service import crear_cliente, listar_clientes, obtener_cliente,obtener_cliente_por_persona_service

cliente_bp = Blueprint('cliente_bp', __name__)

@cliente_bp.route('/clientes', methods=['GET'])
def listar_todos_clientes():
    return listar_clientes()

@cliente_bp.route('/clientes/<int:id_cliente>', methods=['GET'])
def obtener_cliente_por_id(id_cliente):
    return obtener_cliente(id_cliente)

@cliente_bp.route('/clientes/persona/<int:id_persona>', methods=['GET'])
def obtener_cliente_por_persona(id_persona):
    return obtener_cliente_por_persona_service(id_persona)



