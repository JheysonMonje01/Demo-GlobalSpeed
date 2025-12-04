from app.models.gestion_servicio_model import GestionServicio
from app.utils.api_users import obtener_correo_usuario_por_id
from app.extensions import db, logger
from datetime import datetime
from sqlalchemy import and_
from app.models.usuario_pppoe_model import UsuarioPPPoE
from app.utils.api_activar_desactivar import put_configuracion_activar_pppoe,put_configuracion_desactivar_pppoe
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def registrar_evento_gestion(id_usuario_pppoe, id_contrato, estado_servicio, motivo, id_usuario_admin):
    try:
        logger.debug(f"🧩 Valores recibidos -> "
             f"id_usuario_pppoe: {id_usuario_pppoe}, "
             f"id_contrato: {id_contrato}, "
             f"estado_servicio: {estado_servicio}, "
             f"id_usuario_admin: {id_usuario_admin}")
        # Validación básica
        if None in [id_usuario_pppoe, id_contrato, estado_servicio, id_usuario_admin]:
            logger.warning("⚠️ Datos incompletos para registrar la gestión del servicio.")
            return {
                "status": "error",
                "message": "Faltan datos obligatorios para completar la desactivación"
            }, 400

        logger.info(f"📥 Registrando evento de gestión para contrato {id_contrato}, estado: {estado_servicio}")
        # Obtener correo del administrador desde el microservicio de autenticación
        correo_admin = obtener_correo_usuario_por_id(id_usuario_admin) or "desconocido"
        if not correo_admin:
            logger.warning(f"⚠️ No se pudo obtener el correo del usuario con ID {id_usuario_admin}. Se asignará 'desconocido'.")
            correo_admin = "desconocido"
        else:
            logger.info(f"📧 Correo del administrador obtenido: {correo_admin}")

        registro = GestionServicio(
            id_usuario_pppoe=id_usuario_pppoe,
            id_contrato=id_contrato,
            estado_servicio=estado_servicio,
            motivo=motivo,
            usuario_admin_correo=correo_admin,
            fecha_evento=datetime.utcnow()
        )
        logger.info("✅ Evento de gestión del servicio registrado en la base de datos.")
        db.session.add(registro)
        return True, "Evento de gestión registrado correctamente."

    except Exception as e:
        logger.error(f"❌ Error al registrar la gestión del servicio: {str(e)}", exc_info=True)
        return False, f"Error al registrar gestión del servicio: {str(e)}"

def obtener_gestiones_filtradas(filtros):
    query = db.session.query(GestionServicio)

    if filtros.get("id_contrato"):
        query = query.filter(GestionServicio.id_contrato == filtros["id_contrato"])
    if filtros.get("id_usuario_pppoe"):
        query = query.filter(GestionServicio.id_usuario_pppoe == filtros["id_usuario_pppoe"])
    if filtros.get("estado_servicio") is not None:
        query = query.filter(GestionServicio.estado_servicio == filtros["estado_servicio"])
    if filtros.get("usuario_admin_correo"):
        query = query.filter(GestionServicio.usuario_admin_correo.ilike(f"%{filtros['usuario_admin_correo']}%"))
    if filtros.get("fecha_inicio") and filtros.get("fecha_fin"):
        query = query.filter(
            and_(
                GestionServicio.fecha_evento >= filtros["fecha_inicio"],
                GestionServicio.fecha_evento <= filtros["fecha_fin"]
            )
        )

    return query.order_by(GestionServicio.fecha_evento.desc()).all()

def listar_todas_las_gestiones():
    return GestionServicio.query.order_by(GestionServicio.fecha_evento.desc()).all()

def activar_usuario_pppoe(id_usuario_pppoe, id_usuario_admin):
    usuario = UsuarioPPPoE.query.get(id_usuario_pppoe)
    if not usuario:
        logging.warning(f"❌ Usuario PPPoE con ID {id_usuario_pppoe} no encontrado.")
        return {"status": "error", "message": "Usuario PPPoE no encontrado"}, 404

    try:
        # 1. Primero actualizas en la DB
        usuario.estado = True
        db.session.flush()  # ⚠️ Esto asegura que el cambio quede en memoria, pero NO se aplica aún

          # 🔍 Log para depurar los datos enviados al evento de gestión
        logging.warning("📋 Datos enviados a registrar_evento_gestion:")
        logging.warning(f"   ▶ id_usuario_pppoe: {id_usuario_pppoe}")
        logging.warning(f"   ▶ id_contrato: {usuario.id_contrato}")
        logging.warning(f"   ▶ estado_servicio: 0")
        logging.warning(f"   ▶ motivo: Desactivación manual del servicio PPPoE")
        logging.warning(f"   ▶ id_usuario_admin: {id_usuario_admin}")

        ok, msg = registrar_evento_gestion(
            id_usuario_pppoe=id_usuario_pppoe,
            id_contrato=usuario.id_contrato,
            estado_servicio=1,
            motivo="Activacion manual del servicio PPPoE",
            id_usuario_admin=id_usuario_admin
        )
        if not ok:
            db.session.rollback()
            logging.error(f"❌ Error al registrar evento de gestión: {msg}")
            return {"status": "error", "message": msg}, 500

        # 2. Luego, si todo OK en DB, intenta desactivar en MikroTik
        datos_envio = {
            "usuario_pppoe": usuario.usuario_pppoe
        }
        exito, respuesta = put_configuracion_activar_pppoe(datos_envio)

        if not exito:
            db.session.rollback()
            logging.error(f"❌ Error en MikroTik, se revierte la base de datos: {respuesta}")
            return {
                "status": "error",
                "message": respuesta.get("message", "Error en MikroTik")
            }, 500

        # 3. Si MikroTik también OK, finalmente se confirma en la DB
        db.session.commit()
        logging.info(f"✅ Usuario PPPoE ID {id_usuario_pppoe} activado correctamente.")
        return {"status": "success", "message": "Usuario activado correctamente"}, 200

    except Exception as e:
        db.session.rollback()
        logging.exception("❌ Excepción al activar usuario PPPoE:")
        return {"status": "error", "message": str(e)}, 500


    
def desactivar_usuario_pppoe(id_usuario_pppoe, id_usuario_admin):
    usuario = UsuarioPPPoE.query.get(id_usuario_pppoe)
    if not usuario:
        logging.warning(f"❌ Usuario PPPoE con ID {id_usuario_pppoe} no encontrado.")
        return {"status": "error", "message": "Usuario PPPoE no encontrado"}, 404

    try:
        # 1. Primero actualizas en la DB
        usuario.estado = False
        db.session.flush()  # ⚠️ Esto asegura que el cambio quede en memoria, pero NO se aplica aún

          # 🔍 Log para depurar los datos enviados al evento de gestión
        logging.warning("📋 Datos enviados a registrar_evento_gestion:")
        logging.warning(f"   ▶ id_usuario_pppoe: {id_usuario_pppoe}")
        logging.warning(f"   ▶ id_contrato: {usuario.id_contrato}")
        logging.warning(f"   ▶ estado_servicio: 0")
        logging.warning(f"   ▶ motivo: Desactivación manual del servicio PPPoE")
        logging.warning(f"   ▶ id_usuario_admin: {id_usuario_admin}")

        ok, msg = registrar_evento_gestion(
            id_usuario_pppoe=id_usuario_pppoe,
            id_contrato=usuario.id_contrato,
            estado_servicio=0,
            motivo="Desactivación manual del servicio PPPoE",
            id_usuario_admin=id_usuario_admin
        )
        if not ok:
            db.session.rollback()
            logging.error(f"❌ Error al registrar evento de gestión: {msg}")
            return {"status": "error", "message": msg}, 500

        # 2. Luego, si todo OK en DB, intenta desactivar en MikroTik
        datos_envio = {
            "usuario_pppoe": usuario.usuario_pppoe
        }
        exito, respuesta = put_configuracion_desactivar_pppoe(datos_envio)

        if not exito:
            db.session.rollback()
            logging.error(f"❌ Error en MikroTik, se revierte la base de datos: {respuesta}")
            return {
                "status": "error",
                "message": respuesta.get("message", "Error en MikroTik")
            }, 500

        # 3. Si MikroTik también OK, finalmente se confirma en la DB
        db.session.commit()
        logging.info(f"✅ Usuario PPPoE ID {id_usuario_pppoe} desactivado correctamente.")
        return {"status": "success", "message": "Usuario desactivado correctamente"}, 200

    except Exception as e:
        db.session.rollback()
        logging.exception("❌ Excepción al desactivar usuario PPPoE:")
        return {"status": "error", "message": str(e)}, 500

