from flask import Blueprint, request, jsonify
from app.services.persona_service import crear_persona, obtener_persona, actualizar_persona, eliminar_persona, crear_persona_desde_autenticacion, listar_personas_con_filtros

persona_bp = Blueprint('persona', __name__, url_prefix='/personas')
import time
import logging
logging.basicConfig(
    level=logging.INFO,  # Nivel mínimo que se mostrará
    format='%(asctime)s - %(levelname)s - %(message)s'
)
@persona_bp.route('/', methods=['POST'])
def crear():
    data = request.get_json()
    start_time = time.perf_counter()
    end_time = time.perf_counter()
    tiempo_espera = end_time - start_time
    logging.info(f"🕒 Tiempo de espera crear_cliente: {tiempo_espera:.3f} segundos")
    return crear_persona(data)

@persona_bp.route('/<int:id_persona>', methods=['GET'])
def obtener(id_persona):
    return obtener_persona(id_persona)

@persona_bp.route('/<int:id_persona>', methods=['PUT'])
def actualizar(id_persona):
    data = request.get_json()
    return actualizar_persona(id_persona, data)

@persona_bp.route('/<int:id_persona>', methods=['DELETE'])
def eliminar(id_persona):
    return eliminar_persona(id_persona)




"""*******************************************************************"""


"""from flask import Blueprint, request, jsonify
from app.services.persona_service import crear_persona_desde_autenticacion

persona_bp = Blueprint('persona', __name__)

@persona_bp.route('/personas', methods=['POST'])
def crear_persona_externa():
    try:
        data = request.get_json()
        resultado = crear_persona_desde_autenticacion(data)
        return jsonify(resultado), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
"""
"""*******************************************************************"""
from marshmallow import ValidationError

@persona_bp.route('/personas/externo', methods=['POST'])
def crear_persona_externa():
    try:
        data = request.get_json()
        start_time = time.perf_counter()
        
        resultado = crear_persona_desde_autenticacion(data)
        end_time = time.perf_counter()
        tiempo_espera = end_time - start_time
        logging.info(f"🕒 Tiempo de espera crear_cliente: {tiempo_espera:.3f} segundos")
        return jsonify(resultado), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except ValidationError as ve:
        return jsonify({"error": ve.messages}), 400
    except Exception as ex:
        return jsonify({"error": "Error inesperado", "detalle": str(ex)}), 500
    
    
    
"""*******************************************************************"""    
"""ENDPOINT PARA ACTUALIZAR PERSONA DESDE AUTENTICACION"""

from app.services.sincronizacion_service import sincronizar_persona_completa

@persona_bp.route('/personas/sincronizar-completo', methods=['PUT'])
def sincronizar_persona_completa_endpoint():
    data = request.get_json()
    print("📥 JSON recibido en sincronizar_persona_completa:")
    print(data)  # <-- imprime todo lo que recibe
    return sincronizar_persona_completa(data)

"""*******************************************************************"""

"""ENDPOINT PARA ELIMINAR PERSONA LOGICAMENTE Y FISICAMENTE"""
from app.models.persona_model import Persona
from app.db import db

@persona_bp.route('/personas/por-usuario/<int:id_usuario>', methods=['DELETE'])
def eliminar_por_id_usuario(id_usuario):
    persona = Persona.query.filter_by(id_usuario=id_usuario).first()

    if not persona:
        return jsonify({
            "mensaje": "No se encontró una persona asociada a este usuario.",
            "nota": "Puede que ya haya sido eliminada previamente o no se haya creado correctamente."
        }), 204  # Mantener 204 pero con contenido explicativo para logs si deseas

    id_persona = persona.id_persona
    entidad_afectada = None

    # Identificar si es cliente, técnico o administrador
    if persona.cliente:
        entidad_afectada = "cliente"
    elif persona.tecnico:
        entidad_afectada = "técnico"
    elif persona.administrador:
        entidad_afectada = "administrador"

    db.session.delete(persona)
    db.session.commit()

    mensaje = {
        "mensaje": "Persona eliminada correctamente.",
        "id_usuario": id_usuario,
        "id_persona": id_persona,
        "rol_afiliado": entidad_afectada or "No tenía rol asociado",
        "nota": "Se eliminó también la entidad asociada gracias a la relación ON DELETE CASCADE." if entidad_afectada else "Solo existía como persona sin entidad asociada."
    }

    return jsonify(mensaje), 200


"""********************************************************************"""

"""ENDPOINT PARA EL METODO GET CON FILTROS AVANZADOS"""

@persona_bp.route('/personas-filtros', methods=['GET'])
def listar_personas_filtrado():
    return listar_personas_con_filtros()


""""********************************************************************"""
"""ENDPOINT PARA OBTENER LA INFO PARA EL  MICROSERVICIO DE GESTION_SERVICIO"""

from app.services.persona_service import obtener_persona_por_id_cliente

@persona_bp.route('/por-cliente/<int:id_cliente>', methods=['GET'])
def obtener_persona_por_cliente(id_cliente):
    return obtener_persona_por_id_cliente(id_cliente)


