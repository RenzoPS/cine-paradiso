import requests

from cine_paradiso_web.constants import API_TIMEOUT_SEGUNDOS, API_URL, TOKEN_COOKIE_NOMBRE

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

def cancelar_compra(id_compra, token):
    """
    Pide a la API que cancele la compra. Devuelve (True, None) si salió bien o (False, motivo) si falló, con un texto para mostrarle al usuario.
    """
    try:
        respuesta = requests.post(
            f'{API_URL}/compras/{id_compra}/cancelar',
            cookies={TOKEN_COOKIE_NOMBRE: token},
            timeout=API_TIMEOUT_SEGUNDOS,
        )
    except requests.RequestException:
        return False, 'No pudimos cancelar tu compra. Intentá de nuevo en unos minutos'

    if respuesta.ok:
        return True, None
    return False, _motivo_del_error(respuesta)


def abandonar_compra(id_compra, token):
    """
    Pide a la API que borre una compra que todavía no se pagó. Devuelve (True, None) si salió bien o (False, motivo) si falló.
    """
    try:
        respuesta = requests.delete(
            f'{API_URL}/compras/{id_compra}',
            cookies={TOKEN_COOKIE_NOMBRE: token},
            timeout=API_TIMEOUT_SEGUNDOS,
        )
    except requests.RequestException:
        return False, 'No pudimos abandonar tu compra. Intentá de nuevo en unos minutos'

    if respuesta.ok:
        return True, None
    return False, _motivo_del_error(respuesta)

def obtener_compra(id_compra, token):
    """
    Pide a la API los datos de la compra. Devuelve (compra, None) si salió bien o (None, motivo) si falló, con un texto para mostrarle al usuario.
    """
    try:
        respuesta = requests.get(
            f'{API_URL}/compras/{id_compra}',
            cookies={TOKEN_COOKIE_NOMBRE: token},
            timeout=API_TIMEOUT_SEGUNDOS,
        )
    except requests.RequestException:
        return None, 'No pudimos mostrar tu compra. Intentá de nuevo en unos minutos'

    if respuesta.ok:
        return respuesta.json(), None
    return None, _motivo_del_error(respuesta)


def _motivo_del_error(respuesta):
    try:
        return respuesta.json()['errors'][0]['description']
    except (ValueError, KeyError, IndexError):
        return MOTIVO_POR_DEFECTO