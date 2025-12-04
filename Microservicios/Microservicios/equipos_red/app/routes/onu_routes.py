'''from flask import Blueprint, request, jsonify
from app.services.onu_service import (
    crear_onu,
    obtener_onu,
    registrar_onu_detectada,
    actualizar_onu,
    eliminar_onu,
    deducir_puerto_pon_desde_caja
)
from app.schemas.onu_schema import ONUSchema
from marshmallow import ValidationError

onu_bp = Blueprint("onu_bp", __name__, url_prefix="/onus")
schema = ONUSchema()
schema_many = ONUSchema(many=True)

# Crear ONU
@onu_bp.route("", methods=["POST"])
def crear():
    try:
        data = request.get_json()
        validado = schema.load(data)
        nueva_onu = crear_onu(validado)
        return schema.jsonify(nueva_onu), 201
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Listar todas las ONUs (con filtros opcionales)
@onu_bp.route("", methods=["GET"])
def listar():
    try:
        filtros = request.args.to_dict()
        onus = obtener_onu(filtros)
        return schema_many.jsonify(onus), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Obtener ONU por ID
@onu_bp.route("/<int:id_onu>", methods=["GET"])
def obtener(id_onu):
    try:
        onu = obtener_onu(id_onu)
        if not onu:
            return jsonify({"error": "ONU no encontrada"}), 404
        return schema.jsonify(onu), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Actualizar ONU por ID
@onu_bp.route("/<int:id_onu>", methods=["PUT"])
def actualizar(id_onu):
    try:
        data = request.get_json()
        validado = schema.load(data, partial=True)
        onu_actualizada = actualizar_onu(id_onu, validado)
        return schema.jsonify(onu_actualizada), 200
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Eliminar ONU (lógico)
@onu_bp.route("/<int:id_onu>", methods=["DELETE"])
def eliminar(id_onu):
    try:
        eliminado = eliminar_onu(id_onu)
        if eliminado:
            return jsonify({"message": "ONU eliminada correctamente"}), 200
        return jsonify({"error": "ONU no encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@onu_bp.route("/registrar-detectada", methods=["POST"])
def registrar_detectada():
    try:
        data = request.get_json()

        required = [
            "serial_number", "modelo_onu", "ont_id",
            "numero_puerto_nap", "id_caja", "id_contrato"
        ]
        if not all(k in data for k in required):
            return jsonify({"error": "Faltan campos requeridos"}), 400

        # Si no viene explícitamente el puerto PON, lo deducimos desde la caja
        if "id_puerto_pon_olt" not in data:
            data["id_puerto_pon_olt"] = deducir_puerto_pon_desde_caja(data["id_caja"])

        nueva_onu = registrar_onu_detectada(data)
        return jsonify(schema.dump(nueva_onu)), 201

    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500'''

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.schemas.onu_schema import ONUSchema
from app.services.onu_service import (
    registrar_onu,
    listar_onus,
    obtener_onu_por_id,
    actualizar_onu,
    eliminar_onu,
    filtrar_onus, 
    asignar_onu_a_contrato,
    obtener_onu_por_contrato,
    actualizar_estado_onu
)
from app.extensions import db
from app.models.onu import ONU

onu_bp = Blueprint("onu_bp", __name__, url_prefix="/onus")

# Inicializar esquema
onu_schema = ONUSchema(context={"session": db.session})
onus_schema = ONUSchema(many=True)

# Endpoint para registrar una ONU en inventario
@onu_bp.route("", methods=["POST"])
def crear_onu():
    try:
        data = request.get_json()
        # Validación y deserialización (crea un objeto ONU)
        validado = onu_schema.load(data)
        return registrar_onu(validado)
    except ValidationError as err:
        return {"status": "error", "message": err.messages}, 400
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500


# GET /onus - Listar todas
@onu_bp.route("", methods=["GET"])
def get_onus():
    onus, code = listar_onus()
    return onus_schema.dump(onus, many=True), code


# GET /onus/<id_onu>
@onu_bp.route("/<int:id_onu>", methods=["GET"])
def get_onu(id_onu):
    result, code = obtener_onu_por_id(id_onu)
    if isinstance(result, dict):
        return result, code
    return onu_schema.dump(result), code


# PUT /onus/<id_onu> - Actualizar
@onu_bp.route("/<int:id_onu>", methods=["PUT"])
def put_onu(id_onu):
    try:
        data = request.get_json()
        return actualizar_onu(id_onu, data)
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500


# DELETE /onus/<id_onu> - Eliminar
@onu_bp.route("/<int:id_onu>", methods=["DELETE"])
def delete_onu(id_onu):
    return eliminar_onu(id_onu)

#get de filtros
@onu_bp.route("/filtrar", methods=["GET"])
def filtrar_onus_endpoint():
    try:
        texto = request.args.get("q")          # texto de búsqueda
        estado = request.args.get("estado")    # estado opcional

        onus, code = filtrar_onus(texto, estado)
        if isinstance(onus, dict):  # error
            return onus, code

        return onus_schema.dump(onus, many=True), code
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500
    
#conteo 
@onu_bp.route('/resumen', methods=['GET'])
def obtener_resumen_onus():
    try:
        total = ONU.query.count()
        libres = ONU.query.filter_by(estado='libre').count()
        activas = ONU.query.filter_by(estado='activo').count()

        return jsonify({
            "total": total,
            "libres": libres,
            "activas": activas
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error al obtener resumen: {str(e)}"}), 500



# Endpoint para asignar una ONU
'''@onu_bp.route("/asignar/<int:id_onu>", methods=["PUT"])
def asignar_onu_endpoint(id_onu):
    try:
        data = request.get_json()
        id_contrato = data.get("id_contrato")
        id_caja = data.get("id_caja")
        id_puerto_pon_olt = data.get("id_puerto_pon_olt")
        numero_puerto_nap = data.get("numero_puerto_nap")

        if not all([id_contrato, id_caja, id_puerto_pon_olt, numero_puerto_nap is not None]):
            return {"status": "error", "message": "Faltan datos para asignar la ONU."}, 400

        return asignar_onu(id_onu, id_contrato, id_caja, id_puerto_pon_olt, numero_puerto_nap)

    except Exception as e:
        return {"status": "error", "message": str(e)}, 500
'''
import logging
logging.basicConfig(level=logging.INFO)

from app.models.caja_nap import CajaNAP 


@onu_bp.route('/<int:id_onu>/asignar', methods=['PUT'])
def asignar_onu(id_onu):
    try:
        data = request.get_json()
        logging.info(f"📥 Datos recibidos en PUT /onus/{id_onu}/asignar: {data}")

        id_contrato = data.get("id_contrato")
        id_caja = data.get("id_caja")

        if not all([id_contrato, id_caja]):
            logging.warning("❌ Faltan campos requeridos: id_contrato o id_caja")
            return jsonify({"error": "Faltan campos requeridos"}), 400
        
        caja = CajaNAP.query.get(id_caja)
        if not caja:
            logging.warning(f"❌ Caja con id {id_caja} no encontrada")
            return jsonify({"error": "Caja no encontrada"}), 404

        logging.info("✅ Validación OK. Procediendo a asignar ONU...")

        resultado, mensaje = asignar_onu_a_contrato(id_onu, id_contrato, caja)

        if resultado:
            logging.info(f"✅ ONU asignada correctamente: {mensaje}")
            return jsonify({"message": mensaje}), 200
        else:
            logging.error(f"❌ Error al asignar ONU: {mensaje}")
            return jsonify({"error": mensaje}), 400

    except Exception as e:
        logging.exception("❌ Error inesperado en asignar_onu")
        return jsonify({"error": f"Error interno: {str(e)}"}), 500
    
@onu_bp.route("/validar-ont-id", methods=["GET"])
def validar_ont_id():
    try:
        id_puerto = request.args.get("id_puerto_pon_olt", type=int)
        ont_id = request.args.get("ont_id", type=str)

        if not id_puerto or not ont_id:
            return jsonify({
                "status": "error",
                "message": "Se requieren 'id_puerto_pon_olt' y 'ont_id'."
            }), 400

        existe = ONU.query.filter_by(
            id_puerto_pon_olt=id_puerto,
            ont_id=ont_id
        ).first()

        return jsonify({
            "status": "success",
            "existe": existe is not None
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al validar ont_id: {str(e)}"
        }), 500

# GET /onus/contar/<int:id_puerto_pon_olt>
@onu_bp.route("/contar/<int:id_puerto_pon_olt>", methods=["GET"])
def contar_onus_por_puerto(id_puerto_pon_olt):
    cantidad = ONU.query.filter_by(id_puerto_pon_olt=id_puerto_pon_olt).count()
    return jsonify({"cantidad": cantidad})

from app.schemas.onu_schema import ONUSchema
#get para onus con estado libre
from sqlalchemy import func

@onu_bp.route('/disponibles', methods=['GET'])
def obtener_onus_disponibles():
    try:
        onus_libres = ONU.query.filter(func.lower(func.trim(ONU.estado)) == 'libre').all()
        return jsonify(onu_schema.dump(onus_libres, many=True)), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

from app.utils.api_clientes import obtener_contrato_por_id, obtener_nombre_completo_cliente
from app.models.puerto_pon_olt import PuertoPONOLT
from app.models.tarjeta_olt import TarjetaOLT

@onu_bp.route("/enriquecidas", methods=["GET"])
def listar_onus_enriquecidas():
    try:
        onus = ONU.query.all()
        resultado = []

        for onu in onus:
            # Obtener puerto PON
            puerto = PuertoPONOLT.query.get(onu.id_puerto_pon_olt)
            numero_puerto = puerto.numero_puerto if puerto else None

            # Obtener tarjeta OLT y slot
            slot_numero = None
            id_olt = None
            if puerto and puerto.id_tarjeta_olt:
                tarjeta = TarjetaOLT.query.get(puerto.id_tarjeta_olt)
                if tarjeta:
                    slot_numero = tarjeta.slot_numero
                    id_olt = tarjeta.id_olt

            # Obtener cliente desde contrato
            contrato = obtener_contrato_por_id(onu.id_contrato)
            cliente_nombre = None
            if contrato:
                id_cliente = contrato.get("id_cliente")
                cliente_nombre = obtener_nombre_completo_cliente(id_cliente)

            resultado.append({
                "id_contrato": onu.id_contrato,
                "slot_numero": slot_numero,
                "numero_puerto": numero_puerto,
                "ont_id": onu.ont_id,
                "serial": onu.serial,
                "cliente": cliente_nombre,
                "estado": onu.estado,
                "id_olt": id_olt
            })

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# GET /onus/contrato/<int:id_contrato> - Obtener ONU por contrato
@onu_bp.route("/contrato/<int:id_contrato>", methods=["GET"])
def get_onu_por_contrato(id_contrato):
    try:
        onu = obtener_onu_por_contrato(id_contrato)
        if not onu:
            return jsonify({"error": "ONU no encontrada para este contrato"}), 404
        return onu_schema.dump(onu), 200
    except Exception as e:
        return jsonify({"error": f"Error al obtener ONU: {str(e)}"}), 500
    
@onu_bp.put('/<int:id_onu>/estado')
def actualizar_estado(id_onu):
    data = request.get_json()
    nuevo_estado = data.get("estado")

    if not nuevo_estado:
        return {"status": "error", "message": "El campo 'estado' es obligatorio"}, 400

    return actualizar_estado_onu(id_onu, nuevo_estado)