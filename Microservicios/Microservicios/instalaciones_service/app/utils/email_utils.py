from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from sendgrid.helpers.mail.mail import Mail
import os, base64
import logging
logger = logging.getLogger(__name__)
from python_http_client.exceptions import HTTPError

def enviar_correo_tecnico(destinatario, nombre_tecnico, apellido_tecnico, nombre_cliente, apellido_cliente, ubicacion, ruta_pdf):
    try:
        if not os.path.exists(ruta_pdf):
            logger.error(f"📄 El archivo PDF no existe en la ruta: {ruta_pdf}")
            return
         
        with open(ruta_pdf, "rb") as f:
            contenido = f.read()
            adjunto = Attachment()
            adjunto.file_content = FileContent(base64.b64encode(contenido).decode())
            adjunto.file_type = FileType('application/pdf')
            adjunto.file_name = FileName(os.path.basename(ruta_pdf))
            adjunto.disposition = Disposition('attachment')

        asunto = "Nueva orden de instalación asignada"
        mensaje_html = f"""
        <p>
            Estimado/a {nombre_tecnico} {apellido_tecnico},<br><br>
            Se le ha asignado una nueva orden de instalación al cliente {nombre_cliente} {apellido_cliente} 
            en la ubicación <strong>{ubicacion}</strong>.<br><br>
            Por favor revise el archivo adjunto.<br><br>
            Saludos,<br>
            Equipo de Global Speed
        </p>
        """

        email = Mail(
            from_email=os.getenv("SENDGRID_SENDER_EMAIL"),
            to_emails=destinatario,
            subject=asunto,
            html_content=mensaje_html
        )
        email.attachment = adjunto

        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(email)
        logger.info(f"✅ Correo enviado con éxito. Status: {response.status_code}")

    except HTTPError as e:
        logger.error("❌ Error HTTP al enviar correo con SendGrid:")
        logger.error(f"Status Code: {e.status_code}")
        logger.error(f"Body: {e.body}")
        logger.error(f"Headers: {e.headers}")
    except Exception as e:
        logger.exception("❌ Error inesperado al enviar correo al técnico")
        raise
