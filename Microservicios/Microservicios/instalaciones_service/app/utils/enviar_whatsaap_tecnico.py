import os
from twilio.rest import Client

def enviar_whatsapp_tecnico(telefono, nombre_tecnico, apellido_tecnico, nombre_cliente, apellido_cliente, ubicacion):
    try:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        sandbox_number = os.getenv("TWILIO_WHATSAPP_SANDBOX")  # 'whatsapp:+14155238886'

        client = Client(account_sid, auth_token)

        mensaje = (
            f"Hola {nombre_tecnico} {apellido_tecnico}, "
            f"tienes una nueva orden asignada para instalar a {nombre_cliente} {apellido_cliente} "
            f"en {ubicacion}. Por favor revisa tu correo con el PDF adjunto."
        )

        message = client.messages.create(
            body=mensaje,
            from_=sandbox_number,
            to=f"whatsapp:{telefono}"  # Asegúrate que sea +593XXXXXXXXX
        )

        return True, f"Mensaje enviado con SID: {message.sid}"

    except Exception as e:
        return False, f"Error al enviar mensaje WhatsApp: {str(e)}"
