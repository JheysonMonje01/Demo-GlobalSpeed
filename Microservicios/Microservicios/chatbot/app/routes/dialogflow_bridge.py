from flask import Blueprint, request, jsonify
import dialogflow_v2 as dialogflow
import os
import uuid

dialogflow_bridge_bp = Blueprint("dialogflow_bridge", __name__, url_prefix="/dialogflow")

@dialogflow_bridge_bp.route("/consulta", methods=["POST"])
def consulta_dialogflow():
    data = request.get_json()
    mensaje = data.get("mensaje", "")
    session_id = data.get("session_id", str(uuid.uuid4()))

    if not mensaje:
        return jsonify({"error": "El campo 'mensaje' es obligatorio."}), 400

    try:
        respuesta = detectar_intent(mensaje, session_id)
        texto = respuesta.query_result.fulfillment_text
        return jsonify({"respuesta": texto})
    except Exception as e:
        return jsonify({"error": f"No se pudo procesar la solicitud: {str(e)}"}), 500

def detectar_intent(texto, session_id):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/credentials/chatbotglobalspeed-omcn-da91a0d9182d.json"
    project_id = "chatbotglobalspeed-omcn"

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.types.TextInput(text=texto, language_code="es")
    query_input = dialogflow.types.QueryInput(text=text_input)

    response = session_client.detect_intent(session=session, query_input=query_input)
    return response
