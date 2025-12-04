from app.utils.planes_client import obtener_planes_disponibles, generar_contexto_planes
from flask import request

def respuesta_planes_disponibles():
    planes = obtener_planes_disponibles()
    if not planes:
        return "Actualmente no hay planes disponibles. Por favor, vuelve a consultar más tarde."

    mensaje = "📡 Nuestros planes de internet disponibles son:\n"
    for plan in planes:
        nombre = plan.get("nombre_plan", "Plan sin nombre")
        precio = plan.get("precio", "Precio no disponible")
        velocidad = plan.get("velocidad_subida", "")  # asumimos que address_list indica velocidad

        if velocidad:
            mensaje += f"• {nombre}: {velocidad} Mbps por ${precio}.\n"
        else:
            mensaje += f"• {nombre}: {velocidad} Mbps por ${precio}.\n"
    
    return mensaje.strip()

def generar_respuesta_claude(pregunta_usuario, contexto):
    mensaje = (
        f"Contexto:\n{contexto}\n\n"
        f"Usuario pregunta: {pregunta_usuario}\n\n"
        "Con base en los planes disponibles, recomienda el más adecuado y responde de forma clara, natural y profesional, sin inventar detalles técnicos que no están en el contexto."
    )

    respuesta = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": os.getenv("CLAUDE_API_KEY"),
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": "claude-3-sonnet-20240229",
            "messages": [{"role": "user", "content": mensaje}],
            "max_tokens": 500,
            "temperature": 0.7
        }
    )
    return respuesta.json()["content"][0]["text"]
