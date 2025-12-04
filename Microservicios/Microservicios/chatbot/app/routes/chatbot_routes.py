from flask import Blueprint, request, jsonify
from app.services.empresa_service import (
    obtener_nombre_empresa,
    obtener_direccion_empresa,
    obtener_correos_empresa,
    obtener_telefonos_empresa,
    obtener_representante_empresa,
    obtener_contactos_empresa,
    obtener_horario_atencion
)
from app.services.planes_service import respuesta_planes_disponibles,generar_contexto_planes
from app.utils.claude_client import generar_respuesta_claude
from app.utils.cobertura_utils import obtener_lat_lng_desde_direccion, verificar_cobertura_por_coordenadas

chatbot_bp = Blueprint("chatbot", __name__)
import logging

# Configura el nivel de logging (opcionalmente puedes guardar en archivo también)
logging.basicConfig(level=logging.INFO)


@chatbot_bp.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    intent = req['queryResult']['intent']['displayName']

    if intent == "NombreEmpresa":
        return jsonify({"fulfillmentText": obtener_nombre_empresa()})

    elif intent == "DireccionEmpresa":
        return jsonify({"fulfillmentText": obtener_direccion_empresa()})

    elif intent == "CorreosEmpresa":
        return jsonify({"fulfillmentText": obtener_correos_empresa()})

    elif intent == "TelefonosEmpresa":
        return jsonify({"fulfillmentText": obtener_telefonos_empresa()})

    elif intent == "RepresentanteEmpresa":
        return jsonify({"fulfillmentText": obtener_representante_empresa()})
    
    elif intent == "ContactosEmpresa":
        return jsonify({"fulfillmentText": obtener_contactos_empresa()})
    
    elif intent == "HorarioAtencion":  # 👈 nuevo intent
        return jsonify({"fulfillmentText": obtener_horario_atencion()})

    elif intent == "PlanesDisponibles":
        planes = respuesta_planes_disponibles()
        seguimiento = "¿Te interesa contratar alguno de estos planes?"
        return jsonify({
            "fulfillmentText": f"{planes}\n\n{seguimiento}"
        })
    
    elif intent == "ConfirmarContratacion":
        direccion = obtener_direccion_empresa()
        telefonos = obtener_telefonos_empresa()
        horario = obtener_horario_atencion()

        return jsonify({
            "fulfillmentText": (
                f"¡Excelente! 😊 Puedes acercarte a nuestra oficina ubicada en:\n📍 {direccion}\n\n"
                f"También puedes contactarnos al 📞 {telefonos}\n\n"
                f"Nuestro horario de atención es: 🕐 {horario}\n\n"
                "¿Te gustaría que verifiquemos si tienes cobertura en tu ubicación?"
            )
        })
    
    elif intent == "ConfirmarVerificacionCobertura":
        return jsonify({
            "fulfillmentText": (
                "📍 Perfecto. Por favor, indícame tu dirección exacta para que podamos verificar si tienes cobertura "
                "en esa zona. Puedes escribirla en este formato: calle, número, barrio o sector."
            )
        })

    elif intent == "VerificarCoberturaPorDireccion":
        direccion = req['queryResult']['parameters'].get('location')
        logging.info(f"👉 Intent detectado: {intent}")
        logging.info(f"📦 Parámetros: {direccion}")
        if not direccion:
            return jsonify({"fulfillmentText": "No entendí la dirección. ¿Podrías repetirla?"})

        lat, lng = obtener_lat_lng_desde_direccion(direccion)
        if not lat or not lng:
            return jsonify({"fulfillmentText": "No pude encontrar esa dirección. Verifica que esté bien escrita."})

        tiene_cobertura = verificar_cobertura_por_coordenadas(lat, lng)
        if tiene_cobertura:
            return jsonify({"fulfillmentText": "✅ ¡Sí tienes cobertura en esa dirección! Puedes acercarte a nuestra oficina para contratar el servicio."})
        else:
            return jsonify({"fulfillmentText": "❌ Lo siento, actualmente no tenemos cobertura en esa ubicación. Puedes consultarnos por otras zonas."})


    elif intent == "PedirRecomendacion":
        mensaje_usuario = req['queryResult'].get('queryText', '')
        contexto = generar_contexto_planes()
        respuesta = generar_respuesta_claude(mensaje_usuario, contexto)
        return jsonify({"fulfillmentText": respuesta})

    return jsonify({"fulfillmentText": "No entendí tu solicitud. ¿Puedes repetirla?"})
