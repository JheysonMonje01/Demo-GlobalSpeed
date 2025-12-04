from app.models.usuario_pppoe_model import UsuarioPPPoE
from app.utils.api_config import post_configuracion_trafico_pppoe
import logging

def obtener_trafico_usuario_pppoe_por_id(id_usuario_pppoe):
    try:
        logging.info(f"🔍 [GESTIÓN] Buscando usuario PPPoE con ID: {id_usuario_pppoe}")
        usuario = UsuarioPPPoE.query.get(id_usuario_pppoe)

        if not usuario:
            logging.warning(f"⚠️ [GESTIÓN] Usuario PPPoE con ID {id_usuario_pppoe} no encontrado")
            return {"status": "error", "message": "Usuario PPPoE no encontrado"}, 404

        logging.info(f"✅ [GESTIÓN] Usuario encontrado: {usuario.usuario_pppoe}")

        # Preparar solicitud al microservicio configuración
        logging.info("📡 [GESTIÓN] Consultando microservicio de configuración...")
        logging.info(f"📦 [GESTIÓN] Enviando datos: usuario_pppoe = {usuario.usuario_pppoe}")

        resultado, estado = post_configuracion_trafico_pppoe(usuario.usuario_pppoe)

        logging.info(f"📥 [GESTIÓN] Código de respuesta: {estado}")
        logging.info(f"📥 [GESTIÓN] Cuerpo de respuesta: {resultado}")

        return resultado, estado

    except Exception as e:
        logging.exception("❌ [GESTIÓN] Error inesperado al obtener tráfico PPPoE")
        return {"status": "error", "message": str(e)}, 500