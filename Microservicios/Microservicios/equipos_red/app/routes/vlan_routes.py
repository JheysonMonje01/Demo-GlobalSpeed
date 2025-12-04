from flask import Blueprint, request, jsonify
from app.services.vlan_service import crear_vlan, obtener_vlans_filtradas, listar_todas_las_vlans
from app.schemas.vlan_schema import VLANSchema

vlan_bp = Blueprint('vlan_bp', __name__, url_prefix='/api')

vlan_schema = VLANSchema()

@vlan_bp.route('/crear-vlan', methods=['POST'])
def crear():
    data = request.get_json()

    numero_vlan = data.get("numero_vlan")
    nombre = data.get("nombre")
    interface = data.get("interface_destino")
    id_mikrotik = data.get("id_mikrotik")


    exito, resultado = crear_vlan(numero_vlan, nombre, interface, id_mikrotik)

    if exito:
        return jsonify(vlan_schema.dump(resultado)), 201
    else:
        return jsonify({"status": "error", "message": resultado}), 400


"""ENDPOINT PARA BUSCAR POR FILTRO"""

vlan_schema = VLANSchema()
vlan_schema_many = VLANSchema(many=True)

@vlan_bp.route('/vlans', methods=['GET'])
def listar_vlans():
    filtros = request.args.to_dict()
    exito, resultado = obtener_vlans_filtradas(filtros)

    if exito:
        return jsonify(vlan_schema_many.dump(resultado)), 200
    else:
        return jsonify({ "status": "error", "message": resultado }), 400


"""ENDPOINT PARA RETORNAR AL MICROSERVICION DE CONFIGURACION LA ID_VLAN CREADA"""
from app.services.vlan_service import obtener_vlan_por_id

@vlan_bp.route('/vlan/<int:id_vlan>', methods=['GET'])
def obtener_vlan(id_vlan):
    exito, resultado = obtener_vlan_por_id(id_vlan)
    
    if exito:
        return jsonify(vlan_schema.dump(resultado)), 200
    else:
        return jsonify({"status": "error", "message": resultado}), 404


@vlan_bp.route('/vlans/todas', methods=['GET'])
def get_vlans_sin_filtro():
    exito, resultado = listar_todas_las_vlans()
    if exito:
        return jsonify(vlan_schema_many.dump(resultado)), 200
    else:
        return jsonify({"status": "error", "message": resultado}), 500
