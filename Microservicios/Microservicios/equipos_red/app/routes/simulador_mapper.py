'''from flask import Blueprint, jsonify, request
from app.models.tarjeta_olt import TarjetaOLT
from app.models.puerto_pon_olt import PuertoPONOLT
from app.models.onu import ONU
from app.schemas.onu_schema import ONUSchema
from app.services.onu_service import registrar_onu_detectada, actualizar_onu_existente
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import abort
import requests

schema = ONUSchema()
onu_sim_bp = Blueprint("onu_sim_bp", __name__, url_prefix="/onus")


def parsear_fsp(fsp):
    try:
        frame, slot, puerto = map(int, fsp.strip().split("/"))
        return frame, slot, puerto
    except Exception:
        return None, None, None


def buscar_tarjeta_por_slot(slot_numero):
    return TarjetaOLT.query.filter_by(slot_numero=slot_numero).first()


def buscar_id_puerto_pon_olt(slot, numero_puerto):
    tarjeta = buscar_tarjeta_por_slot(slot)
    if not tarjeta:
        abort(404, description=f"No se encontró tarjeta OLT con slot {slot}")

    puerto_pon = PuertoPONOLT.query.filter_by(
        id_tarjeta_olt=tarjeta.id_tarjeta_olt,
        numero_puerto=numero_puerto
    ).first()

    if not puerto_pon:
        abort(404, description=f"No se encontró puerto PON número {numero_puerto} en la tarjeta slot {slot}")

    return puerto_pon.id_puerto_pon_olt


def construir_data_desde_simulador(onu_simulada, id_caja=None, numero_puerto_nap=1):
    _, slot, puerto = parsear_fsp(onu_simulada["f_s_p"])

    data = {
        "serial_number": onu_simulada["ont_sn"],
        "modelo_onu": "HG8546M",
        "ont_id": onu_simulada["ont_id"],
        "id_puerto_pon_olt":  buscar_id_puerto_pon_olt(slot, puerto)
    }

    if id_caja:
        data["numero_puerto_nap"] = numero_puerto_nap
        data["id_caja"] = id_caja

    return data


@onu_sim_bp.route("/registrar-desde-simulador", methods=["POST"])
def registrar_desde_simulador():
    try:
        datos = request.get_json(silent=True) or {}

        # Acepta que vengan como null o no vengan
        id_caja = datos.get("id_caja")  # puede ser None
        numero_puerto_nap = datos.get("numero_puerto_nap")  # puede ser None

        response = requests.get("http://host.docker.internal:5005/api/onus-detectadas")
        onus_simuladas = response.json()

        nuevas_onus = []
        errores = []

        for onu in onus_simuladas:
            serial = onu.get("ont_sn")
            existente = ONU.query.filter_by(serial_number=serial).first()

            try:
                # Aquí pasas los valores, aunque sean None
                data = construir_data_desde_simulador(onu, id_caja, numero_puerto_nap)

                if existente:
                    actualizar_onu_existente(existente, data)
                else:
                    nueva_onu = registrar_onu_detectada(data)
                    nuevas_onus.append(schema.dump(nueva_onu))

            except Exception as e:
                errores.append({
                    "ont_sn": serial,
                    "f_s_p": onu.get("f_s_p"),
                    "error": str(e)
                })

        return jsonify({
            "registradas": nuevas_onus,
            "errores": errores
        }), 201

    except SQLAlchemyError as e:
        return jsonify({"error": f"Error de base de datos: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

from app.extensions import db
from app.models.caja_nap import CajaNAP

@onu_sim_bp.route("/<int:id_onu>/asignar-caja", methods=["PUT"])
def asignar_caja_a_onu(id_onu):
    data = request.get_json()
    id_caja = data.get("id_caja")
    numero_puerto_nap = data.get("numero_puerto_nap")

    onu = ONU.query.get(id_onu)
    if not onu:
        abort(404, description="ONU no encontrada")
        
    if not CajaNAP.query.get(id_caja):
        abort(404, description="Caja NAP no encontrada")


    onu.id_caja = id_caja
    onu.numero_puerto_nap = numero_puerto_nap

    db.session.commit()

    return jsonify({"mensaje": "Caja y puerto NAP asignados correctamente", "onu": schema.dump(onu)})
'''