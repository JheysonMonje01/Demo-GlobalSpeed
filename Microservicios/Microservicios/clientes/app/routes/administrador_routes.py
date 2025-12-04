

from flask import Blueprint, request
from app.services.administrador_service import crear_administrador, listar_administradores, obtener_administrador

administrador_bp = Blueprint('administrador_bp', __name__)

@administrador_bp.route('/administradores', methods=['GET'])
def listar_todos_administradores():
    return listar_administradores()

@administrador_bp.route('/administradores/<int:id_administrador>', methods=['GET'])
def obtener_administrador_por_id(id_administrador):
    return obtener_administrador(id_administrador)




