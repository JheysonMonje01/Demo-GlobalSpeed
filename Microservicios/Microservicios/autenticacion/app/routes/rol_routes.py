from flask import Blueprint, request
from app.services.rol_service import crear_rol, buscar_roles

rol_bp = Blueprint('rol', __name__)

@rol_bp.route('/roles', methods=['POST'])
def crear():
    data = request.get_json()
    return crear_rol(data)


"""CONSULTAR POR EL ID ROL LOS DATOS DEL ROL"""

@rol_bp.route('/roles/filtrado', methods=['GET'])
def get_roles_filtrados():
    return buscar_roles()




