import os
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
from app.models.contrato_model import Contrato
from app.extensions import db
from datetime import datetime, timedelta

from app.utils.configuracion_empresa import obtener_datos_empresa
from app.utils.clientes_persona import obtener_datos_cliente
from app.utils.planes_cliente import obtener_datos_plan
from app.utils.generador_contrato import generar_contrato_pdf
from app.utils.onu_utils import obtener_datos_onu
from app.utils.geocoding import obtener_direccion_desde_coordenadas  # ✅ NUEVO
from app.utils.api_ordenes import crear_orden_instalacion
from app.utils.api_pagos_utils import notificar_creacion_orden_pago

import requests
import logging
logging.basicConfig(level=logging.INFO)
from sqlalchemy import and_


def crear_contrato(data):
    try:
        logging.info("🟡 Iniciando creación de contrato...")
        id_empresa = data.get("id_empresa")
        id_cliente = data.get("id_cliente")
        id_plan = data.get("id_plan")
        fecha_fin = data.get("fecha_fin_contrato")
        id_onu = data.get("id_onu")
        lat = float(data.get("lat"))
        lng = float(data.get("lng"))


        logging.info(f"📥 Datos recibidos: empresa={id_empresa}, cliente={id_cliente}, plan={id_plan}, lat={lat}, lng={lng}")
        if not all([id_empresa, id_cliente, id_plan, lat, lng]):
            raise ValueError("Faltan campos obligatorios: 'id_empresa', 'id_cliente', 'id_plan', 'lat', 'lng'")

        margen_error = 0.00005  # ~5 metros
        contrato_existente = Contrato.query.filter(
            Contrato.id_cliente == id_cliente,
            and_(
                Contrato.latitud.between(lat - margen_error, lat + margen_error),
                Contrato.longitud.between(lng - margen_error, lng + margen_error)
            )
        ).first()

        if contrato_existente:
            raise ValueError("Ya existe un contrato para este cliente en la misma ubicación.")
        
        logging.info("✅ Verificación de contrato duplicado completada.")

        # ✅ Obtener datos externos
        empresa = obtener_datos_empresa(id_empresa)
        
        if "error" in empresa:
            raise ValueError(empresa["error"])

        cliente = obtener_datos_cliente(id_cliente)
        logging.info(f"✅ Datos cliente: {cliente}")
        if "error" in cliente:
            raise ValueError(cliente["error"])

        plan = obtener_datos_plan(id_plan)
        logging.info(f"✅ Datos plan: {plan}")
        if "error" in plan:
            raise ValueError(plan["error"])
        
        onu = obtener_datos_onu(id_onu)
        logging.info(f"✅ Datos ONU: {onu}")
        if "error" in onu:
            raise ValueError(onu["error"])

        # ✅ Obtener dirección legible desde lat/lng
        ubicacion = obtener_direccion_desde_coordenadas(lat, lng)
        logging.info(f"📍 Dirección desde coordenadas: {ubicacion}")

        # Calcular fecha fin contrato = 1 año después
        fecha_fin = datetime.utcnow().date().replace(year=datetime.utcnow().year + 1)

        # ✅ Crear contrato inicial
        nuevo_contrato = Contrato(
            id_cliente=id_cliente,
            id_plan=id_plan,
            id_empresa=id_empresa,
            ubicacion=ubicacion,
            fecha_fin_contrato=fecha_fin,
            fecha_creacion=datetime.utcnow(),
            latitud=lat,
            longitud=lng
        )
        db.session.add(nuevo_contrato)
        db.session.flush()

        logging.info(f"🆕 Contrato preliminar creado con ID {nuevo_contrato.id_contrato}")

        # ✅ Buscar caja más cercana
        CUBRIMIENTO_URL = os.getenv("CAJAS_SERVICE_URL", "http://localhost:5004")
        r = requests.get(f"{CUBRIMIENTO_URL}/cajas-nap/disponible-cercana", params={"lat": lat, "lng": lng}, timeout=5)
        r.raise_for_status()
        info_caja = r.json()["caja_mas_cercana"]

        id_caja = info_caja["id_caja"]
        #id_puerto_pon_olt = info_caja["id_puerto_pon"]
        #numero_puerto_nap = info_caja["puerto_disponible"]


        # ✅ Confirmar contrato antes de asignar ONU
        db.session.commit()  # 🟢 COMMIT AQUÍ para evitar error de clave foránea

        # ✅ Enviar petición para asignar la ONU
        ONU_SERVICE_URL = os.getenv("ONUS_SERVICE_URL", "http://localhost:5004")
        payload_onu = {
            "id_contrato": nuevo_contrato.id_contrato,
            "id_caja": id_caja
        }
        logging.info(f"Payload para asignar ONU: {payload_onu}")
        r_onu = requests.put(f"{ONU_SERVICE_URL}/onus/{id_onu}/asignar", json=payload_onu)

        r_onu.raise_for_status()

        # ✅ Generar PDF del contrato
        nombre_archivo = f"contrato_{nuevo_contrato.id_contrato}.pdf"
        ruta_carpeta = os.path.join(current_app.root_path, "static", "contratos")
        os.makedirs(ruta_carpeta, exist_ok=True)
        ruta_absoluta = os.path.join(ruta_carpeta, nombre_archivo)
        ruta_relativa = f"/static/contratos/{nombre_archivo}"

        logging.info(f"🖨️ Generando contrato PDF en: {ruta_absoluta}")
        try:
            generar_contrato_pdf(cliente, empresa, plan, nuevo_contrato, ruta_absoluta, onu)
        except Exception as e:
            logging.error(f"❌ Error al generar PDF: {e}")
            raise RuntimeError(f"No se pudo generar el contrato PDF: {str(e)}")
        
        nuevo_contrato.url_archivo = f"http://localhost:5006{ruta_relativa}"
        logging.info(f"📄 PDF asignado a contrato: {nuevo_contrato.url_archivo}")

        db.session.commit()  # Guardar la URL del archivo PDF

        # ✅ Enviar intención de crear orden de pago
        respuesta_pago = notificar_creacion_orden_pago(
            id_contrato=nuevo_contrato.id_contrato,
            id_plan=id_plan,
            fecha_inicio=nuevo_contrato.fecha_creacion.date().isoformat()
        )

        if respuesta_pago["status"] == "error":
            current_app.logger.warning(
                f"⚠️ No se pudo generar orden de pago automáticamente: {respuesta_pago.get('message')}"
            )


        # 🔧 Crear orden de instalación automáticamente
        ok, resultado = crear_orden_instalacion(nuevo_contrato.id_contrato)
        if not ok:
            logging.warning(f"⚠️ Contrato creado pero no se pudo generar la orden: {resultado}")
        else:
            logging.info(f"📦 Orden de instalación generada exitosamente: {resultado}")

        logging.info("✅ Contrato creado exitosamente con PDF.")
        return nuevo_contrato
        

    except (ValueError, KeyError) as err:
        db.session.rollback()
        logging.error(f"⚠️ Error de validación: {str(err)}")
        raise ValueError(f"Error en los datos: {str(err)}")

    except SQLAlchemyError as db_err:
        db.session.rollback()
        logging.error(f"🛑 Error en la base de datos: {str(db_err)}")
        raise SQLAlchemyError(f"Error en la base de datos: {str(db_err)}")

    except Exception as e:
        db.session.rollback()
        logging.error(f"🚨 Error inesperado: {str(e)}")
        raise Exception(f"Error inesperado al crear el contrato: {str(e)}")

from app.models.contrato_model import Contrato
from app.schemas.contrato_schema import contratos_schema
from flask import jsonify

def obtener_contratos_por_cliente_service(id_cliente):
    contratos = Contrato.query.filter_by(id_cliente=id_cliente).all()
    return jsonify(contratos_schema.dump(contratos)), 200
