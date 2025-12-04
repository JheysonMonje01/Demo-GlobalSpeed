from flask import Blueprint, jsonify
from app.services.generar_ordenes_pago import generar_ordenes_futuras
orden_pago_bp = Blueprint("orden_pago_bp", __name__, url_prefix="/ordenes")

@orden_pago_bp.route('/ordenes/generar-futuras', methods=['POST'])
def generar_ordenes_automaticas():
    resultado = generar_ordenes_futuras()
    if resultado["status"] == "success":
        return jsonify({
            "status": "success",
            "message": f"{resultado['total_creadas']} órdenes creadas automáticamente."
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": resultado["message"]
        }), 500
