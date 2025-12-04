import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def enviar_correo_recuperacion(destinatario, token):
    api_key = os.getenv("SENDGRID_API_KEY")
    remitente = os.getenv("SENDGRID_SENDER_EMAIL")

    if not api_key or not remitente:
        raise ValueError("Falta SENDGRID_API_KEY o SENDGRID_SENDER_EMAIL en variables de entorno.")

    enlace = f"http://localhost:5173/restablecer?token={token}"
    contenido = f"""
    Hola,

    Recibimos una solicitud para restablecer tu contraseña.

    Haz clic en el siguiente enlace para continuar:
    {enlace}

    Si tú no solicitaste esto, puedes ignorar este mensaje.

    Saludos,
    El equipo de Global Speed
    """

    message = Mail(
        from_email=remitente,
        to_emails=destinatario,
        subject="Recuperación de contraseña - Global Speed",
        plain_text_content=contenido,
        html_content=contenido.replace('\n', '<br>')  # agregado para evitar rechazo si falta html
    )

    sg = SendGridAPIClient(api_key)
    response = sg.send(message)
    return response.status_code
