from flask import Blueprint, request, jsonify
from app.services.caja_nap_service import (
    crear_caja_nap,
    obtener_cajas_nap,
    obtener_caja_por_id,
    actualizar_caja_nap,
    eliminar_caja_nap
)
from app.schemas.caja_nap_schema import CajaNAPSchema
from marshmallow import ValidationError
from app.extensions import db
from app.utils.distancia import obtener_distancia_google_maps
from app.models.caja_nap import CajaNAP

caja_nap_bp = Blueprint("caja_nap_bp", __name__, url_prefix="/cajas-nap")
schema = CajaNAPSchema(context={"session": db.session})
schema_many = CajaNAPSchema(many=True)

# Crear caja NAP
@caja_nap_bp.route("", methods=["POST"])
def crear():
    try:
        data = request.get_json()
        validado = schema.load(data, session=db.session)
        nueva_caja = crear_caja_nap(validado)
        return jsonify(schema.dump(nueva_caja)), 201
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Obtener todas las cajas NAP (con filtros)
@caja_nap_bp.route("", methods=["GET"])
def listar():
    try:
        filtros = request.args.to_dict()
        cajas = obtener_cajas_nap(filtros)
        return jsonify(schema_many.dump(cajas)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Obtener caja por ID
@caja_nap_bp.route("/<int:id_caja>", methods=["GET"])
def obtener(id_caja):
    try:
        caja = obtener_caja_por_id(id_caja)
        if not caja:
            return jsonify({"error": "Caja NAP no encontrada"}), 404
        return jsonify(schema.dump(caja)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Actualizar caja por ID
@caja_nap_bp.route("/<int:id_caja>", methods=["PUT"])
def actualizar(id_caja):
    try:
        data = request.get_json()
        validado = schema.load(data, partial=True, session=db.session)
        caja_actualizada = actualizar_caja_nap(id_caja, validado)
        return jsonify(schema.dump(caja_actualizada)), 200
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Eliminar caja (lógica)
@caja_nap_bp.route("/<int:id_caja>", methods=["DELETE"])
def eliminar(id_caja):
    try:
        logico = request.args.get("fisico", "false").lower() != "true"
        resultado = eliminar_caja_nap(id_caja, logico=logico)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

import math

def calcular_bounding_box(lat, lng, radio_metros):
    R = 6378137  # Radio de la Tierra en metros
    delta_lat = (radio_metros / R) * (180 / math.pi)
    delta_lng = (radio_metros / (R * math.cos(math.pi * lat / 180))) * (180 / math.pi)

    lat_min = lat - delta_lat
    lat_max = lat + delta_lat
    lng_min = lng - delta_lng
    lng_max = lng + delta_lng

    return lat_min, lat_max, lng_min, lng_max


import logging
logging.basicConfig(level=logging.INFO)
from app.services.puerto_pon_olt_service import obtener_puerto
#obtener la caja mas cercana a una ubicacion
@caja_nap_bp.route('/disponible-cercana', methods=['GET'])
def obtener_caja_mas_cercana():
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))

        # Calcular límites de búsqueda (bounding box de 400 metros)
        lat_min, lat_max, lng_min, lng_max = calcular_bounding_box(lat, lng, 400)

        # Filtrar cajas solo dentro del área de 400 metros (bounding box)
        cajas = CajaNAP.query.filter(
            CajaNAP.estado == True,
            CajaNAP.latitud >= lat_min,
            CajaNAP.latitud <= lat_max,
            CajaNAP.longitud >= lng_min,
            CajaNAP.longitud <= lng_max
        ).all()
        logging.error(f"🔍 Cajas dentro del radio estimado: {len(cajas)}")
        if not cajas:
            return jsonify({"message": "No hay cajas activas registradas"}), 404

        candidatas = []
        comparaciones = []

        print(f"🔎 Total de cajas activas encontradas: {len(cajas)}")

        for caja in cajas:
            capacidad = caja.capacidad_puertos_cliente or 0
            ocupados = caja.puertos_ocupados or 0
            disponibles = capacidad - ocupados

            print(f"📦 Caja '{caja.nombre_caja_nap}' → capacidad: {capacidad}, ocupados: {ocupados}, disponibles: {disponibles}")

            if disponibles <= 0:
                print(f"⚠️ Caja descartada por no tener puertos disponibles.")
                continue

            try:
                distancia_km = obtener_distancia_google_maps(lat, lng, caja.latitud, caja.longitud)
                distancia_m = round(distancia_km * 1000)

                candidatas.append((distancia_km, caja, disponibles, distancia_m))
                comparaciones.append({
                    "id_caja": caja.id_caja,
                    "nombre": caja.nombre_caja_nap,
                    "disponibles": disponibles,
                    "distancia_m": distancia_m
                })

            except Exception as e:
                print(f"❌ Error al calcular distancia con Google Maps para {caja.nombre_caja_nap}: {e}")
                continue

        if not candidatas:
            return jsonify({
                "message": "No hay cajas con puertos disponibles",
                "comparacion_debug": comparaciones
            }), 400

        # Ordenar y obtener la mejor
        candidatas.sort(key=lambda x: x[0])
        distancia_km, caja_cercana, disponibles, distancia_m = candidatas[0]

        # Obtener puerto PON relacionado
        id_puerto_pon = caja_cercana.id_puerto_pon_olt
        puerto = obtener_puerto(id_puerto_pon)

        if not puerto:
            return jsonify({"message": "Puerto PON de la caja no encontrado"}), 404

        numero_puerto = puerto.numero_puerto
        slot_numero = puerto.tarjeta.slot_numero if puerto.tarjeta else None

        return jsonify({
            "caja_mas_cercana": {
                "id_caja": caja_cercana.id_caja,
                "nombre_caja": caja_cercana.nombre_caja_nap,
                "latitud": caja_cercana.latitud,
                "longitud": caja_cercana.longitud,
                "puerto_disponible": caja_cercana.puertos_ocupados + 1,
                "id_puerto_pon": id_puerto_pon,
                "numero_puerto": numero_puerto,
                "slot_numero": slot_numero,
                "distancia_km": round(distancia_km, 3),
                "distancia_m": distancia_m,
                "puertos_totales": caja_cercana.capacidad_puertos_cliente,
                "puertos_ocupados": caja_cercana.puertos_ocupados,
                "puertos_disponibles": disponibles
            },
            "comparacion": sorted(comparaciones, key=lambda x: x["distancia_m"])
        }), 200

    except Exception as e:
        return jsonify({"message": f"Error interno: {str(e)}"}), 500
