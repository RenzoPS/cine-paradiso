import logging
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Template

from ..constants import MAIL_FROM, MAIL_HOST, MAIL_PASSWORD, MAIL_PORT, MAIL_USER

logger = logging.getLogger(__name__)


def _obtener_config():
    """Devuelve la configuración SMTP, o None si falta algo."""
    obligatorias = {
        "MAIL_HOST": MAIL_HOST,
        "MAIL_USER": MAIL_USER,
        "MAIL_PASSWORD": MAIL_PASSWORD,
        "MAIL_FROM": MAIL_FROM,
    }
    faltantes = []
    for nombre, valor in obligatorias.items():
        if not valor:
            faltantes.append(nombre)

    if faltantes:
        logger.error("Falta configurar el mail: %s", ", ".join(faltantes))
        return None
    return {
        "host": MAIL_HOST,
        "port": MAIL_PORT,
        "user": MAIL_USER,
        "password": MAIL_PASSWORD,
        "remitente": MAIL_FROM,
    }


def armar_mail(plantilla, datos):
    """Arma el HTML de un mail: reemplaza los {{ ... }} de la plantilla por los datos."""
    return Template(plantilla, autoescape=True).render(**datos)


def enviar_mail(destinatario, asunto, cuerpo_html, imagen_qr=None):
    """Envía un mail HTML. Devuelve True si se envió y False si falló, nunca lanza error."""
    config = _obtener_config()
    if config is None:
        return False

    mensaje = MIMEMultipart("related")
    mensaje["Subject"] = asunto
    mensaje["From"] = config["remitente"]
    mensaje["To"] = destinatario
    mensaje.attach(MIMEText(cuerpo_html, "html", "utf-8"))

    if imagen_qr:
        imagen = MIMEImage(imagen_qr, "png")
        imagen.add_header("Content-ID", "<qr>")
        imagen.add_header("Content-Disposition", "inline", filename="qr.png")
        mensaje.attach(imagen)
        
    try:
        with smtplib.SMTP(config["host"], config["port"], timeout=10) as servidor:
            servidor.starttls()
            servidor.login(config["user"], config["password"])
            servidor.send_message(mensaje)
        return True
    except (smtplib.SMTPException, OSError):
        logger.exception("No se pudo enviar el mail a %s", destinatario)
        return False