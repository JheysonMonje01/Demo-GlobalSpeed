from flask import Blueprint, request, jsonify
from app.utils.api_equipos_red import obtener_datos_olt
from app.utils.ssh_huawei import probar_conexion_olt_con_credenciales
from app.services.olt.ont_service import ejecutar_comando_ont_completo

olt_bp = Blueprint('olt', __name__, url_prefix='/olt')

@olt_bp.route('/test-conexion-olt/<int:id_olt>', methods=['GET'])
def test_conexion_olt(id_olt):
    datos = obtener_datos_olt(id_olt)
    if not datos:
        return jsonify({
            "status": "error",
            "message": f"No se encontraron datos de la OLT con ID {id_olt}"
        }), 404

    resultado = probar_conexion_olt_con_credenciales(
        host=datos.get("ip_gestion"),
        username=datos.get("usuario_gestion"),
        password=datos.get("contrasena_gestion")
    )

    if resultado.get("status") == "success":
        return jsonify({
            "status": "success",
            "message": f"✅ Conexión SSH exitosa con la OLT {datos.get('marca')} - {datos.get('modelo')}"
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": f"❌ No se pudo conectar a la OLT: {resultado.get('message')}"
        }), 500


@olt_bp.route('/olt/ejecutar-comandos-ont', methods=['POST'])
def ejecutar_comandos_ont():
    data = request.get_json()

    id_olt = data.get("id_olt")
    if not id_olt:
        return jsonify({
            "status": "error",
            "message": "El campo 'id_olt' es obligatorio."
        }), 400

    # Obtener la configuración de la OLT desde el microservicio equipos_red
    olt_config = obtener_datos_olt(id_olt)
    if not olt_config:
        return jsonify({
            "status": "error",
            "message": f"No se encontró la OLT con id {id_olt}"
        }), 404

    exito, resultado = ejecutar_comando_ont_completo(data, olt_config)

    if exito:
        return jsonify({
            "status": "success",
            "message": resultado
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "Error al ejecutar comandos en OLT",
            "detalle": resultado
        }), 502