import base64, requests

from cine_paradiso_web.constants import API_TIMEOUT_SEGUNDOS, API_URL, TOKEN_COOKIE_NOMBRE
from cine_paradiso_web.services.api_service import llamar_api

MOTIVO_POR_DEFECTO = 'No pudimos confirmar tu compra. Intentá de nuevo en unos minutos'

def confirmar_compra(id_compra, token):
    """
    Pide a la API que confirme la compra. Devuelve (factura, None) si salió bien o (None, motivo) si falló, con un texto para mostrarle al usuario.
    """
    try:
        respuesta = requests.post(
            f'{API_URL}/compras/{id_compra}/confirmar',
            cookies={TOKEN_COOKIE_NOMBRE: token},
            timeout=API_TIMEOUT_SEGUNDOS,
        )
    except requests.RequestException:
        return None, MOTIVO_POR_DEFECTO

    if respuesta.ok:
        return respuesta.json(), None
    return None, _motivo_del_error(respuesta)


def obtener_qr_base64(id_compra, token):
    try:
        respuesta = requests.get(
            f'{API_URL}/compras/{id_compra}/qr',
            cookies={TOKEN_COOKIE_NOMBRE: token},
            timeout=API_TIMEOUT_SEGUNDOS,
        )
    except requests.RequestException:
        return None

    if respuesta.ok:
        return base64.b64encode(respuesta.content).decode('ascii')
    return None


def validar_ingreso_qr(qr_token, id_funcion):
    return llamar_api(
        'POST',
        'compras/validar',
        json={'qr_token': qr_token, 'id_funcion': id_funcion},
    )


def _motivo_del_error(respuesta):
    try:
        return respuesta.json()['errors'][0]['description']
    except (ValueError, KeyError, IndexError):
        return MOTIVO_POR_DEFECTO