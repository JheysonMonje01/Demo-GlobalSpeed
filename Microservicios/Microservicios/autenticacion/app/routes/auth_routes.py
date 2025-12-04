import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_services import register_user, login_user, buscar_usuarios, actualizar_usuario, cambiar_contrasena, solicitar_recuperacion, restablecer_contrasena, refresh_token, logout, eliminar_usuario, eliminar_refresh_token, eliminar_usuario_total

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    return register_user(data)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    return login_user(data)

@auth_bp.route('/validate-token', methods=['GET'])
@jwt_required()
def validate_token():
    usuario = json.loads(get_jwt_identity())  # ✅ decodificar
    return jsonify({
        "mensaje": "Token válido. Acceso concedido",
        "usuario": usuario
    }), 200



"""ENDPOINT PARA EL METODO GET DE USUARIOS"""

@auth_bp.route('/usuarios/filtrado', methods=['GET'])
def get_usuarios_filtrados():
    return buscar_usuarios()



"""ENDPOINT PARA ACTUALIZAR USUARIO"""

@auth_bp.route('/usuarios/<int:id_usuario>', methods=['PUT'])
def update_usuario(id_usuario):
    data = request.get_json()
    return actualizar_usuario(id_usuario, data)



"""###############################################################################"""
"""ACTUALIZAR CONTRASEÑA DEL USUARIO"""
from app.services.auth_services import cambiar_contrasena

@auth_bp.route('/usuarios/<int:id_usuario>/cambiar-password', methods=['PUT'])
def cambiar_password(id_usuario):
    data = request.get_json()
    return cambiar_contrasena(id_usuario, data)

"""###############################################################################"""


"""$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"""

@auth_bp.route('/usuarios/<int:id_usuario>', methods=['DELETE'])
def eliminar(id_usuario):
    return eliminar_usuario(id_usuario)


"""$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"""


@auth_bp.route('/usuarios/eliminar-total/<int:id_usuario>', methods=['DELETE'])
def eliminar_total(id_usuario):
    return eliminar_usuario_total(id_usuario)

"""################################################################################"""





""" ENDPOINT PARA LA RECUPERACION DE CONTRASEÑA """

@auth_bp.route('/recuperar', methods=['POST'])
def recuperar():
    data = request.get_json()
    return solicitar_recuperacion(data)


"""ENDPOINT PARA CAMBIAR CONTRASEÑA"""

@auth_bp.route('/restablecer', methods=['POST'])
def restablecer():
    data = request.get_json()
    return restablecer_contrasena(data)


"""ENDPOINT PARA EL REFRESH TOKEN Y LOGOUT"""

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    data = request.get_json()
    return refresh_token(data)

@auth_bp.route('/logout', methods=['POST'])
def logout_view():
    data = request.get_json()
    return logout(data)



import time
import logging
"""***********************************************************************"""
from app.services.auth_services import register_user_con_persona
@auth_bp.route('/register-con-persona', methods=['POST'])
def register_con_persona():
    data = request.get_json()
    start_time = time.perf_counter()
    end_time = time.perf_counter()
    tiempo_espera = end_time - start_time
    logging.info(f"🕒 Tiempo de espera crear_cliente: {tiempo_espera:.3f} segundos")
    return register_user_con_persona(data)



"""***********************************************************************"""

from app.services.auth_services import completar_persona

@auth_bp.route('/completar-persona', methods=['POST'])
def completar_persona_endpoint():
    data = request.get_json()
    return completar_persona(data)



"""***********************************************************************"""

"""ENDPOINT PARA ACTUALIZAR USUARIO DESDE EL SERVICIO DE AUTENTICACION"""

from app.services.auth_services import actualizar_usuario

@auth_bp.route('/usuarios-personas/<int:id_usuario>', methods=['PUT'])
def actualizar_usuario_endpoint(id_usuario):
    data = request.get_json()
    return actualizar_usuario(id_usuario, data)


"""***********************************************************************"""

"""ENDPOINTS PARA ELIMINAR USUARIOS LOGICAMENTE Y FISICAMENTE"""

from app.services.auth_services import eliminar_usuario_logico, eliminar_usuario_fisico

@auth_bp.route('/usuarios-persona-eliminar/<int:id_usuario>', methods=['DELETE'])
def eliminar_usuario_logicamente(id_usuario):
    return eliminar_usuario_logico(id_usuario)


@auth_bp.route('/usuarios-persona-eliminar/<int:id_usuario>/permanente', methods=['DELETE'])
def eliminar_usuario_fisicamente(id_usuario):
    return eliminar_usuario_fisico(id_usuario)


"""************************************************************************"""

from app.services.auth_services import obtener_usuario_por_id
@auth_bp.route("/usuarios/<int:id_usuario>", methods=["GET"])
def obtener_usuario(id_usuario):
    respuesta, codigo = obtener_usuario_por_id(id_usuario)
    return jsonify(respuesta), codigo