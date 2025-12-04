



from flask import Blueprint, request
from app.services.tecnico_service import crear_tecnico, listar_tecnicos, obtener_tecnico, actualizar_estado, obtener_tecnico_por_persona

tecnico_bp = Blueprint('tecnico_bp', __name__)

@tecnico_bp.route('/tecnicos', methods=['GET'])
def listar_todos_tecnicos():
    return listar_tecnicos()

@tecnico_bp.route('/tecnicos/<int:id_tecnico>', methods=['GET'])
def obtener_tecnico_por_id(id_tecnico):
    return obtener_tecnico(id_tecnico)

@tecnico_bp.route('/tecnicos/<int:id_tecnico>/estado', methods=['PUT'])
def actualizar_estado_tecnico(id_tecnico):
    data = request.get_json()
    return actualizar_estado(id_tecnico, data)

@tecnico_bp.route('/tecnicos', methods=['POST'])
def crear_nuevo_tecnico():
    data = request.get_json()
    return crear_tecnico(data)

@tecnico_bp.route('/tecnicos/persona/<int:id_persona>', methods=['GET'])
def obtener_tecnico_por_id_persona(id_persona):
    return obtener_tecnico_por_persona(id_persona)