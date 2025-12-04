from flask import Blueprint, jsonify
from app.services.mikrotik.interfaces_services import obtener_interfaces_mikrotik

interface_bp = Blueprint("interface_bp", __name__, url_prefix="/mikrotik")

@interface_bp.route("/interfaces/<int:id_mikrotik>", methods=["GET"])
def listar_interfaces(id_mikrotik):
    exito, resultado = obtener_interfaces_mikrotik(id_mikrotik)
    if exito:
        return jsonify({"interfaces": resultado}), 200
    else:
        return jsonify({"status": "error", "message": resultado}), 400
