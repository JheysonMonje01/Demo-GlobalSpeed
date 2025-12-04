from flask import Blueprint, request, jsonify, send_file, current_app,  send_from_directory
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.models.contrato_model import Contrato
import os
from app.extensions import db
from datetime import datetime

from app.schemas.contrato_schema import ContratoSchema
from app.schemas.contrato_schema import contrato_schema, contratos_schema
from app.services.contrato_service import crear_contrato, obtener_contratos_por_cliente_service

contrato_bp = Blueprint("contrato_bp", __name__, url_prefix="/contratos")
contrato_schema = ContratoSchema()

CONTRATOS_DIR = os.path.join(os.getcwd(), 'static', 'contratos')
import time
import logging

@contrato_bp.route("", methods=["POST"])
def crear():
    try:
        start_time = time.perf_counter()
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "No se proporcionaron datos en el cuerpo de la solicitud."
            }), 400

        contrato = crear_contrato(data)
        end_time = time.perf_counter()
        tiempo_espera = end_time - start_time
        logging.info(f"🕒 Tiempo de espera crear_contrato: {tiempo_espera:.3f} segundos")
        
        return jsonify({
            "status": "success",
            "message": "Contrato creado exitosamente.",
            "data": contrato_schema.dump(contrato)
        }), 201

    except ValidationError as err:
        return jsonify({
            "status": "error",
            "message": "Error de validación.",
            "errors": err.messages
        }), 400

    except ValueError as err:
        return jsonify({
            "status": "error",
            "message": str(err)
        }), 400

    except SQLAlchemyError as err:
        return jsonify({
            "status": "error",
            "message": "Error en la base de datos.",
            "details": str(err)
        }), 500

    except Exception as err:
        return jsonify({
            "status": "error",
            "message": "Ocurrió un error inesperado.",
            "details": str(err)
        }), 500

#ENDPOINT PARA DESCARGAR UN CONTRATO
@contrato_bp.route("/descargar/<path:filename>", methods=["GET"])
def descargar_contrato(filename):
    try:
        return send_from_directory(CONTRATOS_DIR, filename, as_attachment=True)
    except FileNotFoundError:
        return {"status": "error", "message": "Archivo no encontrado"}, 404

#ENDPOINT PARA VER CONTRATO
@contrato_bp.route('/ver-contrato/<path:filename>', methods=['GET'])
def ver_contrato(filename):
    if not filename.endswith('.pdf'):
        return {"status": "error", "message": "Formato no permitido"}, 400

    try:
        return send_from_directory(CONTRATOS_DIR, filename, as_attachment=False)
    except FileNotFoundError:
        return {"status": "error", "message": "Archivo no encontrado"}, 404

@contrato_bp.route('', methods=['GET'])
def listar_contratos():
    contratos = Contrato.query.all()
    return jsonify(contratos_schema.dump(contratos)), 200

@contrato_bp.route('/<int:id_contrato>', methods=['GET'])
def obtener_contrato_por_id(id_contrato):
    contrato = Contrato.query.get(id_contrato)
    if not contrato:
        return jsonify({"message": "Contrato no encontrado", "status": "error"}), 404
    return jsonify(contrato_schema.dump(contrato)), 200

#INSERTAR CONTRATO
@contrato_bp.route('/<int:id_contrato>/reemplazar-pdf', methods=["PUT"])
def reemplazar_pdf(id_contrato):
    contrato = Contrato.query.get(id_contrato)
    if not contrato:
        return jsonify({"status": "error", "message": "Contrato no encontrado"}), 404

    if 'archivo' not in request.files:
        return jsonify({"status": "error", "message": "Archivo no proporcionado"}), 400

    archivo = request.files['archivo']
    if archivo.filename == '':
        return jsonify({"status": "error", "message": "Nombre de archivo vacío"}), 400

    nombre_pdf = f"contrato_{id_contrato}.pdf"
    ruta_guardar = os.path.join(CONTRATOS_DIR, nombre_pdf)
    archivo.save(ruta_guardar)

    contrato.url_archivo = f"http://localhost:5006/static/contratos/{nombre_pdf}"
    contrato.fecha_modificacion = datetime.utcnow()
    db.session.commit()

    return jsonify({"status": "success", "message": "PDF reemplazado exitosamente"})


from app.utils.geolocalizacion import obtener_direccion_google
@contrato_bp.route('/ubicacion', methods=['GET'])
def obtener_ubicacion():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not lat or not lon:
        return jsonify({"status": "error", "message": "Latitud y longitud son obligatorias"}), 400

    try:
        ubicacion = obtener_direccion_google(lat, lon)
        if not ubicacion:
            return jsonify({"status": "error", "message": "No se pudo obtener la ubicación"}), 404

        return jsonify({
            "status": "success",
            "message": "Ubicación obtenida correctamente",
            "datos": ubicacion
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Error al obtener ubicación",
            "detalles": str(e)
        }), 500
    
@contrato_bp.route('/cliente/<int:id_cliente>', methods=['GET'])
def obtener_contratos_por_cliente(id_cliente):
    return obtener_contratos_por_cliente_service(id_cliente)
