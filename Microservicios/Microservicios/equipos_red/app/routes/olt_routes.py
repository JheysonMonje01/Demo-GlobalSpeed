from flask import Blueprint, request, jsonify
from app.services.olt_service import (
    crear_olt, obtener_olts_filtradas, obtener_olt_por_id,
    actualizar_olt, eliminar_olt
)
from app.schemas.olt_schema import OLTSchema
from werkzeug.exceptions import BadRequest
import paramiko
from app.models.olt import OLT

olt_bp = Blueprint('olt_bp', __name__, url_prefix='/olts')
olt_schema = OLTSchema()
olt_schema_many = OLTSchema(many=True)

@olt_bp.route('', methods=['POST'])
def crear():
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("El cuerpo de la solicitud está vacío o mal formado.")
        olt = crear_olt(data)
        return jsonify(olt_schema.dump(olt)), 201
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400

@olt_bp.route('', methods=['GET'])
def listar():
    filtros = request.args.to_dict()
    olts = obtener_olts_filtradas(filtros)
    return jsonify(olt_schema_many.dump(olts)), 200

@olt_bp.route('/<int:id_olt>', methods=['GET'])
def obtener(id_olt):
    olt = obtener_olt_por_id(id_olt)
    return jsonify(olt_schema.dump(olt)), 200

@olt_bp.route('/<int:id_olt>', methods=['PUT'])
def actualizar(id_olt):
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("El cuerpo de la solicitud está vacío o mal formado.")
        olt_actualizada = actualizar_olt(id_olt, data)
        return jsonify(olt_schema.dump(olt_actualizada)), 200
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400

@olt_bp.route('/<int:id_olt>', methods=['DELETE'])
def eliminar(id_olt):
    eliminar_olt(id_olt)
    return jsonify({"message": "OLT eliminada correctamente"}), 200

from app.ssh_manager import ejecutar_comando_ssh
from app.olt_parser import parsear_salida_autofind

@olt_bp.route("/<int:id_olt>/probar-conexion", methods=["GET"])
def probar_conexion(id_olt):
    olt = OLT.query.get(id_olt)
    if not olt:
        return jsonify({"error": "OLT no encontrada"}), 404

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=olt.ip_gestion,
            username=olt.usuario_gestion,
            password=olt.contrasena_gestion,
            timeout=5
        )
        client.close()
        return jsonify({
            "conexion_exitosa": True,
            "ip": olt.ip_gestion,
            "usuario": olt.usuario_gestion
        }), 200

    except Exception as e:
        return jsonify({
            "conexion_exitosa": False,
            "ip": olt.ip_gestion,
            "error": str(e)
        }), 500
#Listar ONUs detectadas desde la OLT real   
@olt_bp.route("/<int:id_olt>/onus-detectadas", methods=["GET"])
def listar_onus_detectadas_desde_olt(id_olt):
    olt = OLT.query.get(id_olt)
    if not olt:
        return jsonify({"error": "OLT no encontrada"}), 404

    try:
        salida = ejecutar_comando_ssh(
            host=olt.ip_gestion,
            usuario=olt.usuario_gestion,
            contrasena=olt.contrasena_gestion,
            comando="display ont autofind all"
        )
        onus = parsear_salida_autofind(salida)
        return jsonify(onus), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500