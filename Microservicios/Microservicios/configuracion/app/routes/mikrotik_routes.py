from flask import Blueprint, request, jsonify
from app.services.mikrotik.mikrotik_service import actualizar_configuracion,crear_configuracion_mikrotik, obtener_configuracion_por_id, test_conexion_mikrotik_ssh, actualizar_configuracion_mikrotik, obtener_configuraciones_mikrotik, eliminar_fisicamente_mikrotik, eliminar_logicamente_mikrotik, crear_vlan_en_mikrotik, crear_plan_en_mikrotik, crear_pool_en_mikrotik,actualizar_plan_en_mikrotik, eliminar_plan_en_mikrotik, restaurar_plan_en_mikrotik

mikrotik_bp = Blueprint('mikrotik_bp', __name__)

"""ENDPOINT PARA CREAR CONFIGURACION DE MIKROTIK LUEGO DE TESTEARLA"""
@mikrotik_bp.route('/configurar', methods=['POST'])
def configurar_mikrotik():
    data = request.get_json()
    return crear_configuracion_mikrotik(data)

"""ENDPOINT PARA TESTEAR LA CONEXION SSH A MIKROTIK"""
@mikrotik_bp.route('/test-conexion-ssh', methods=['POST'])
def testear_conexion_mikrotik_ssh():
    data = request.get_json()
    return test_conexion_mikrotik_ssh(data)

"""ENDPOINT PARA ACTUALIZAR CONFIGURACION DE MIKROTIK"""
@mikrotik_bp.route('/configurar/<int:id_mikrotik>', methods=['PUT'])
def actualizar_mikrotik(id_mikrotik):
    data = request.get_json()
    return actualizar_configuracion_mikrotik(id_mikrotik, data)

"""ENDPOINT PARA BUSCAR CONFIGURACION DE MIKROTIK"""
@mikrotik_bp.route('/configuraciones', methods=['GET'])
def listar_configuraciones_mikrotik():
    return obtener_configuraciones_mikrotik()

@mikrotik_bp.route('/configuraciones/<int:id_mikrotik>', methods=['GET'])
def obtener_configuracion_mikrotik_por_id(id_mikrotik):
    return obtener_configuracion_por_id(id_mikrotik)

"""ENDPOINTS PARA ELIMINAR CONFIGURACION DE MIKROTIK"""
@mikrotik_bp.route('/configuracion/desactivar/<int:id_mikrotik>', methods=['PUT'])
def desactivar_configuracion(id_mikrotik):
    return eliminar_logicamente_mikrotik(id_mikrotik)

@mikrotik_bp.route('/configuraciones/<int:id_mikrotik>', methods=['PUT'])
def actualizar_configuracion_mikrotik(id_mikrotik):
    data = request.get_json()
    return actualizar_configuracion(id_mikrotik, data)


"""ENDPOINT PARA ELIMINAR FISICAMENTE CONFIGURACION DE MIKROTIK"""
@mikrotik_bp.route('/configuracion/<int:id_mikrotik>', methods=['DELETE'])
def eliminar_configuracion(id_mikrotik):
    return eliminar_fisicamente_mikrotik(id_mikrotik)


"""****************************************************************************"""

"""ENDPOINT PARA LA SOLICITUD DEL MICROSERVICIO DE EQUIPOS_RED"""
"""PERMITIR CREAR UNA VLAN EN MIKROTIK DESDE EL MICROSERVICIO DE CONFIGURACION"""
from app.models.mikrotik_model import MikrotikAPIConfig
from app.utils.ssh_manager import ejecutar_comando_ssh

@mikrotik_bp.route('/crear-vlan', methods=['POST'])
def crear_vlan():
    try:
        data = request.get_json()
        numero_vlan = data.get("numero_vlan")
        nombre = data.get("nombre") or f"vlan{numero_vlan}"  # Nombre opcional
        interface = data.get("interface")

        if not numero_vlan or not interface:
            return jsonify({"status": "error", "message": "Faltan campos requeridos (numero_vlan, interface)"}), 400

        exito, resultado = crear_vlan_en_mikrotik(numero_vlan, nombre, interface)

        if exito:
            return jsonify({"status": "success", "message": resultado}), 201
        else:
            return jsonify({"status": "error", "message": resultado}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error inesperado: {str(e)}"}), 500

"""****************************************************************************"""

"""ENDPOINT PARA CREAR UN PLAN DE INTERNET EN PPPP """
@mikrotik_bp.route('/crear-plan', methods=['POST'])
def crear_plan():
    data = request.json

    exito, resultado = crear_plan_en_mikrotik(data)

    if exito:
        return jsonify({"status": "success", "message": resultado}), 201
    else:
        return jsonify({"status": "error", "message": resultado}), 400


"""****************************************************************************"""
"""ENDPOINT PARA CREAR UN IP POOL EN MIKROTIK"""

@mikrotik_bp.route("/pools", methods=["POST"])
def crear_pool():
    data = request.get_json()

    requerido = ["nombre", "rango_inicio", "rango_fin"]
    if not all(k in data for k in requerido):
        return jsonify({"status": "error", "message": "Faltan campos requeridos"}), 400

    exito, mensaje = crear_pool_en_mikrotik(data)
    if exito:
        return jsonify({"status": "success", "message": mensaje}), 201
    else:
        return jsonify({"status": "error", "message": mensaje}), 500




"""ENDPOINT PARA ACTUALIZAR UN PLAN PPP EXISTENTE EN MIKROTIK"""

@mikrotik_bp.route('/actualizar-plan', methods=['PUT'])
def actualizar_plan():
    data = request.get_json()
    exito, resultado = actualizar_plan_en_mikrotik(data)

    if exito:
        return jsonify({"status": "success", "message": resultado}), 200
    else:
        return jsonify({"status": "error", "message": resultado}), 500



"""ENDPOINT PARA ELIMINAR UN PLAN PPP EN MIKROTIK"""
@mikrotik_bp.route('/eliminar-plan', methods=['DELETE'])
def eliminar_plan():
    data = request.get_json()

    exito, mensaje = eliminar_plan_en_mikrotik(data)
    if exito:
        return jsonify({"status": "success", "message": mensaje}), 200
    else:
        return jsonify({"status": "error", "message": mensaje}), 400


"""ENDPOINT PARA RESTAURAR UN PLAN PPP EN MIKROTIK"""
@mikrotik_bp.route('/restaurar-plan', methods=['POST'])
def restaurar_plan():
    data = request.get_json()
    exito, mensaje = restaurar_plan_en_mikrotik(data)

    if exito:
        return jsonify({"status": "success", "message": mensaje}), 201
    else:
        return jsonify({"status": "error", "message": mensaje}), 400


"""****************************************************************************"""
"""ENDPOINTS PARA CREAR, ELIMINAR Y ACTUALIZAR PERFILES PPPoE EN MIKROTIK"""

from app.services.mikrotik.pppoe_service import crear_perfil_pppoe_en_mikrotik

@mikrotik_bp.route('/crear-perfil-pppoe', methods=['POST'])
def crear_perfil_pppoe():
    data = request.get_json()
    exito, resultado = crear_perfil_pppoe_en_mikrotik(data)
    
    if exito:
        return jsonify(resultado), 200
    else:
        return jsonify({
            "status": "error",
            "message": "Error en MikroTik",
            "detalle": resultado
        }), 502


"""***************************************************************"""

"""ENDPOINT PARA ACTUALIZAR UN PERFIL PPPoE EN MIKROTIK"""

from app.services.mikrotik.pppoe_service import actualizar_perfil_pppoe_en_mikrotik


@mikrotik_bp.route('/actualizar-perfil-pppoe', methods=['PUT'])
def actualizar_perfil_pppoe():
    data = request.get_json()
    exito, resultado = actualizar_perfil_pppoe_en_mikrotik(data)

    if exito:
        return jsonify(resultado), 200
    else:
        return jsonify({
            "status": "error",
            "message": "Error al actualizar perfil en MikroTik",
            "detalle": resultado
        }), 502


"""ENDPOINT PARA ELIMINAR UN USUARIO PPPoE EN MIKROTIK"""
from app.services.mikrotik.pppoe_service import eliminar_usuario_pppoe_en_mikrotik

@mikrotik_bp.route('/eliminar-usuario-pppoe', methods=['DELETE'])
def eliminar_usuario_pppoe():
    try:
        data = request.get_json()
        ok, resultado = eliminar_usuario_pppoe_en_mikrotik(data)
        if ok:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error inesperado: {str(e)}"
        }), 500
    
"""ENDPOINT PARA DESACTIVAR y activar UN USUARIO PPPoE EN MIKROTIK"""
from app.services.mikrotik.pppoe_service import desactivar_usuario_pppoe_en_mikrotik, activar_usuario_pppoe_en_mikrotik

@mikrotik_bp.route("/pppoe/desactivar", methods=["PUT"])
def desactivar_pppoe():
    data = request.get_json()
    ok, respuesta = desactivar_usuario_pppoe_en_mikrotik(data)
    return jsonify(respuesta), (200 if ok else 400)

@mikrotik_bp.route("/pppoe/activar", methods=["PUT"])
def activar_pppoe():
    data = request.get_json()
    ok, respuesta = activar_usuario_pppoe_en_mikrotik(data)
    return jsonify(respuesta), (200 if ok else 400)

"""MONITOREAR TRAFICO DE RED MIKROTIK"""
from app.services.mikrotik.pppoe_service import obtener_trafico_usuario_pppoe

@mikrotik_bp.route("/monitoreo/trafico", methods=["POST"])
def consultar_trafico_pppoe():
    try:
        data = request.get_json()
        success, result = obtener_trafico_usuario_pppoe(data)

        if success:
            return jsonify(result), 200
        elif result.get("status") == "not_found":
            return jsonify(result), 404
        else:
            return jsonify(result), 500

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error interno: {str(e)}"}), 500