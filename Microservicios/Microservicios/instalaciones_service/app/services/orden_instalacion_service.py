from app.extensions import db
from app.models.orden_instalacion import OrdenInstalacion
from app.schemas.orden_instalacion_schema import OrdenInstalacionSchema

from app.utils.cliente_persona import obtener_datos_cliente
from app.utils.tecnico_persona import obtener_datos_tecnico, obtener_tecnico_activo, actualizar_estado_tecnico
from app.utils.contrato_utils import obtener_datos_contrato
from app.utils.onu_utils import obtener_datos_onu, obtener_onu_por_contrato, actualizar_estado_onu
from app.utils.planes_cliente import obtener_datos_plan
from app.utils.generador_ordenes import generar_ordenes_pdf
from datetime import datetime
import requests
import logging
logger = logging.getLogger(__name__)
# Enviar notificación por correo
from app.utils.email_utils import enviar_correo_tecnico
from app.utils.enviar_whatsaap_tecnico import enviar_whatsapp_tecnico
from app.utils.formatos import formatear_telefono_a_internacional
from flask import current_app
import os
EQUIPOS_RED_URL = os.getenv("EQUIPOS_RED_SERVICE_URL")



def crear_orden_instalacion(data):
    try:
        id_contrato = data.get("id_contrato")
        if not id_contrato:
            return {"error": "El campo 'id_contrato' es obligatorio"}, 400
        
         # 🔒 Verificar que no exista una orden ya registrada para ese contrato
        orden_existente = OrdenInstalacion.query.filter_by(id_contrato=id_contrato).first()
        if orden_existente:
            return {"error": f"Ya existe una orden de instalación para el contrato {id_contrato}."}, 409


        # 🔹 Obtener datos del contrato
        contrato = obtener_datos_contrato(id_contrato)
        if "error" in contrato:
            return {"error": contrato["error"]}, 404

        id_cliente = contrato.get("id_cliente")
        id_plan = contrato.get("id_plan")
        id_onu = contrato.get("id_onu")
        ubicacion = contrato.get("ubicacion")

        # 🔹 Obtener datos relacionados
        cliente = obtener_datos_cliente(id_cliente)
        if "error" in cliente:
            return {"error": cliente["error"]}, 404

        plan = obtener_datos_plan(id_plan)
        if "error" in plan:
            return {"error": plan["error"]}, 404

        # Buscar ONU por contrato
        url_onu = f"{EQUIPOS_RED_URL}/onus/contrato/{id_contrato}"
        resp = requests.get(url_onu)

        if resp.status_code != 200:
            return {"error": f"No se encontró la ONU para el contrato {id_contrato}"}, 404

        onu_data = resp.json()
        id_onu = onu_data.get("id_onu")
        if not id_onu:
            return {"error": "La ONU encontrada no tiene ID válido"}, 400
        
        id_caja = onu_data.get("id_caja")

        # 2. Obtener caja NAP
        caja_nap = {}
        if id_caja:
            resp_caja = requests.get(f"{EQUIPOS_RED_URL}/cajas-nap/{id_caja}")
            if resp_caja.status_code == 200:
                caja_nap = resp_caja.json()

        # 🔹 Buscar técnico activo
        tecnico = obtener_tecnico_activo()
        generar_pdf = tecnico is not None

        if tecnico:
            id_tecnico = tecnico.get("id_tecnico") or tecnico.get("id")
            tecnico_data = obtener_datos_tecnico(id_tecnico)
            actualizado = actualizar_estado_tecnico(id_tecnico, "ocupado")
            if not actualizado:
                    return {"error": "No se pudo cambiar el estado del técnico asignado"}, 500
        else:
            id_tecnico = None
            tecnico_data = {}

        # 🔹 Crear orden
        nueva_orden = OrdenInstalacion(
            id_contrato=id_contrato,
            id_tecnico=id_tecnico,
            ubicacion_instalacion=ubicacion,
            estado="en_proceso" if id_tecnico else "pendiente_asignacion",
            
        )

        db.session.add(nueva_orden)
        db.session.commit()

        # 🔹 Si hay técnico → generar documento PDF
        if generar_pdf:
            nueva_orden.fecha_asignacion = datetime.now()
            ruta_pdf = f"/app/archivos/ordenes/orden_{nueva_orden.id_orden}.pdf"
            generar_ordenes_pdf(
                cliente=cliente,
                tecnico=tecnico_data,
                plan=plan,
                contrato=contrato,
                ruta_pdf_final=ruta_pdf,
                onu=onu_data,
                orden=nueva_orden,
                caja_nap=caja_nap
            )
            nueva_orden.documento_pdf = ruta_pdf
            db.session.commit()
            # ✉️ Enviar correo al técnico con el PDF
            try:
                enviar_correo_tecnico(
                    destinatario=tecnico_data.get("correo",""),
                    nombre_tecnico=tecnico_data.get("nombre",""),
                    apellido_tecnico=tecnico_data.get("apellido",""),
                    nombre_cliente=cliente.get("nombre",""),
                    apellido_cliente=cliente.get("apellido",""),
                    ubicacion=contrato.get("ubicacion", ""),
                    ruta_pdf=ruta_pdf
                )

            except Exception as e:
                current_app.logger.error(f"❌ Error al enviar correo al técnico: {str(e)}")
            
            telefono = formatear_telefono_a_internacional(tecnico_data.get("telefono"))
            if telefono:
                ok, mensaje_ws = enviar_whatsapp_tecnico(
                    telefono=telefono,
                    nombre_tecnico=tecnico_data.get("nombre"),
                    apellido_tecnico=tecnico_data.get("apellido"),
                    nombre_cliente=cliente.get("nombre"),
                    apellido_cliente=cliente.get("apellido"),
                    ubicacion=contrato.get("ubicacion")
                )
                if not ok:
                    print("❌ Error al enviar WhatsApp:", mensaje_ws)
            else:
                print("⚠️ Teléfono no válido para WhatsApp")


        schema = OrdenInstalacionSchema()
        return schema.dump(nueva_orden), 201

    except Exception as e:
        db.session.rollback()
        return {"error": f"Error al crear la orden de instalación: {str(e)}"}, 500
    

def asignar_tecnico_a_orden(id_orden, id_tecnico):
    try:
        orden = OrdenInstalacion.query.get(id_orden)
        if not orden:
            return {"error": f"No se encontró la orden con ID {id_orden}"}, 404

        if orden.id_tecnico:
            return {"error": "La orden ya tiene un técnico asignado."}, 400

        # Obtener datos del técnico
        tecnico = obtener_datos_tecnico(id_tecnico)
        if "error" in tecnico:
            return {"error": tecnico["error"]}, 404

        # Obtener datos relacionados
        contrato = obtener_datos_contrato(orden.id_contrato)
        if "error" in contrato:
            return {"error": contrato["error"]}, 404

        cliente = obtener_datos_cliente(contrato.get("id_cliente"))
        if "error" in cliente:
            return {"error": cliente["error"]}, 404

        plan = obtener_datos_plan(contrato.get("id_plan"))
        if "error" in plan:
            return {"error": plan["error"]}, 404

        # Buscar ONU por contrato
        url_onu = f"{EQUIPOS_RED_URL}/onus/contrato/{orden.id_contrato}"
        resp = requests.get(url_onu)

        if resp.status_code != 200:
            return {"error": f"No se encontró la ONU para el contrato {orden.id_contrato}"}, 404

        onu_data = resp.json()
        id_onu = onu_data.get("id_onu")
        if not id_onu:
            return {"error": "La ONU encontrada no tiene ID válido"}, 400
        
        id_caja = onu_data.get("id_caja")

        # 2. Obtener caja NAP
        caja_nap = {}
        if id_caja:
            resp_caja = requests.get(f"{EQUIPOS_RED_URL}/cajas-nap/{id_caja}")
            if resp_caja.status_code == 200:
                caja_nap = resp_caja.json()

        # Asignar técnico y actualizar estado
        orden.id_tecnico = id_tecnico
        orden.estado = "en_proceso"
        orden.fecha_asignacion = datetime.utcnow()

        # Cambiar estado del técnico a ocupado
        actualizado = actualizar_estado_tecnico(id_tecnico, "ocupado")
        if not actualizado:
            db.session.rollback()
            return {"error": "No se pudo actualizar el estado del técnico"}, 500

        # Generar PDF si no existe
        if not orden.documento_pdf:
            ruta_pdf = f"/app/archivos/ordenes/orden_{orden.id_orden}.pdf"
            generar_ordenes_pdf(
                cliente=cliente,
                tecnico=tecnico,
                plan=plan,
                contrato=contrato,
                ruta_pdf_final=ruta_pdf,
                onu=onu_data,
                orden=orden,
                caja_nap=caja_nap
            )
            orden.documento_pdf = ruta_pdf

             # ✅ Enviar notificación al correo del técnico
        enviar_correo_tecnico(
                    destinatario=tecnico.get("correo",""),
                    nombre_tecnico=tecnico.get("nombre",""),
                    apellido_tecnico=tecnico.get("apellido",""),
                    nombre_cliente=cliente.get("nombre",""),
                    apellido_cliente=cliente.get("apellido",""),
                    ubicacion=contrato.get("ubicacion", ""),
                    ruta_pdf=ruta_pdf
        )
        telefono = formatear_telefono_a_internacional(tecnico.get("telefono"))
        if telefono:
                ok, mensaje_ws = enviar_whatsapp_tecnico(
                    telefono=telefono,
                    nombre_tecnico=tecnico.get("nombre"),
                    apellido_tecnico=tecnico.get("apellido"),
                    nombre_cliente=cliente.get("nombre"),
                    apellido_cliente=cliente.get("apellido"),
                    ubicacion=contrato.get("ubicacion")
                )
                if not ok:
                    print("❌ Error al enviar WhatsApp:", mensaje_ws)
        else:
                print("⚠️ Teléfono no válido para WhatsApp")

        db.session.commit()

        db.session.commit()

        schema = OrdenInstalacionSchema()
        return schema.dump(orden), 200

    except Exception as e:
        db.session.rollback()
        return {"error": f"Error al asignar técnico a la orden: {str(e)}"}, 500
    

def finalizar_orden(id_orden):
    try:
        orden = OrdenInstalacion.query.get(id_orden)
        if not orden:
            logger.warning(f"❌ No se encontró la orden con ID {id_orden}")
            return {"error": f"No se encontró la orden con ID {id_orden}"}, 404

        if orden.estado == "finalizado":
            logger.info(f"ℹ️ La orden {id_orden} ya estaba finalizada")
            return {"error": "La orden ya está finalizada"}, 400

        orden.estado = "finalizado"
        orden.fecha_instalacion = datetime.utcnow()

        # ✅ Cambiar el estado del técnico a activo usando función ya existente
        if orden.id_tecnico:
            actualizado = actualizar_estado_tecnico(orden.id_tecnico, "activo")
            if not actualizado:
                db.session.rollback()
                logger.error(f"❌ Error al actualizar estado del técnico con ID {orden.id_tecnico}")
                return {"error": "No se pudo actualizar el estado del técnico"}, 500
        
        # ✅ Obtener ONU por contrato y actualizar si está en preactivación
        # ✅ Verificar si hay ONU vinculada al contrato y actualizar su estado
        if orden.id_contrato:
            logging.info(f"📦 Respuesta de orden : {orden.id_contrato}")

        onu = obtener_onu_por_contrato(orden.id_contrato)

        logging.info(f"📦 Respuesta cruda de ONU para contrato {orden.id_contrato}: {onu}")

        if not onu or not isinstance(onu, dict) or "estado" not in onu:
            logging.warning(f"⚠️ No se encontró ninguna ONU válida asociada al contrato {orden.id_contrato}")
        else:
            logging.info(f"🔍 ONU encontrada para contrato {orden.id_contrato}: estado = {onu.get('estado')}")
            if onu.get("estado") == "preactivacion":
                actualizado = actualizar_estado_onu(onu.get("id_onu"), "activo")
                if actualizado:
                    logging.info(f"✅ Estado de ONU {onu['id_onu']} actualizado a 'activo'")
                else:
                    logging.warning(f"⚠️ Falló al actualizar el estado de la ONU {onu['id_onu']}")
            elif onu.get("estado") == "asigando":
                actualizado = actualizar_estado_onu(onu.get("id_onu"), "instalado")
                if actualizado:
                    logging.info(f"✅ Estado de ONU {onu['id_onu']} actualizado a 'instalado'")
                else:
                    logging.warning(f"⚠️ Falló al actualizar el estado de la ONU {onu['id_onu']}")

        db.session.commit()
        return OrdenInstalacionSchema().dump(orden), 200
    
    except Exception as e:
        db.session.rollback()
        return {"error": f"Error al finalizar la orden: {str(e)}"}, 500
    
def cambiar_tecnico_orden(id_orden, nuevo_id_tecnico):
    try:
        orden = OrdenInstalacion.query.get(id_orden)
        if not orden:
            return {"error": "No se encontró la orden."}, 404

        if orden.estado == "finalizado":
            return {"error": "No se puede cambiar el técnico de una orden finalizada."}, 400
        
        if orden.nuevo_id_tecnico:
            return {"error": "La orden ya tiene un técnico asignado."}, 400

        tecnico_nuevo = obtener_datos_tecnico(nuevo_id_tecnico)
        if "error" in tecnico_nuevo:
            return {"error": tecnico_nuevo["error"]}, 404

        tecnico_anterior_id = orden.id_tecnico
        orden.id_tecnico = nuevo_id_tecnico
        orden.fecha_asignacion = datetime.utcnow()

        # 🟢 Actualizar estados de técnicos
        if tecnico_anterior_id:
            actualizar_estado_tecnico(tecnico_anterior_id, "activo")
        actualizar_estado_tecnico(nuevo_id_tecnico, "ocupado")

        # 🔄 Re-generar PDF con nuevo técnico
        contrato = obtener_datos_contrato(orden.id_contrato)
        cliente = obtener_datos_cliente(contrato.get("id_cliente"))
        plan = obtener_datos_plan(contrato.get("id_plan"))

        url_onu = f"{EQUIPOS_RED_URL}/onus/contrato/{orden.id_contrato}"
        resp = requests.get(url_onu)
        if resp.status_code != 200:
            return {"error": "ONU no encontrada para el contrato"}, 404
        onu = resp.json()

        caja_nap = {}
        id_caja = onu.get("id_caja")
        if id_caja:
            resp_caja = requests.get(f"{EQUIPOS_RED_URL}/cajas-nap/{id_caja}")
            if resp_caja.status_code == 200:
                caja_nap = resp_caja.json()

        ruta_pdf = f"/app/archivos/ordenes/orden_{orden.id_orden}.pdf"
        generar_ordenes_pdf(
            cliente=cliente,
            tecnico=tecnico_nuevo,
            plan=plan,
            contrato=contrato,
            ruta_pdf_final=ruta_pdf,
            onu=onu,
            orden=orden, 
            caja_nap=caja_nap
        )
        orden.documento_pdf = ruta_pdf

        # ✉️ Enviar notificación al nuevo técnico
        enviar_correo_tecnico(
                    destinatario=tecnico_nuevo.get("correo",""),
                    nombre_tecnico=tecnico_nuevo.get("nombre",""),
                    apellido_tecnico=tecnico_nuevo.get("apellido",""),
                    nombre_cliente=cliente.get("nombre",""),
                    apellido_cliente=cliente.get("apellido",""),
                    ubicacion=contrato.get("ubicacion", ""),
                    ruta_pdf=ruta_pdf
        )

        telefono = formatear_telefono_a_internacional(tecnico_nuevo.get("telefono"))
        if telefono:
                ok, mensaje_ws = enviar_whatsapp_tecnico(
                    telefono=telefono,
                    nombre_tecnico=tecnico_nuevo.get("nombre"),
                    apellido_tecnico=tecnico_nuevo.get("apellido"),
                    nombre_cliente=cliente.get("nombre"),
                    apellido_cliente=cliente.get("apellido"),
                    ubicacion=contrato.get("ubicacion")
                )
                if not ok:
                    print("❌ Error al enviar WhatsApp:", mensaje_ws)
        else:
                print("⚠️ Teléfono no válido para WhatsApp")

        db.session.commit()
        return OrdenInstalacionSchema().dump(orden), 200

    except Exception as e:
        db.session.rollback()
        return {"error": f"Error al cambiar técnico: {str(e)}"}, 500
