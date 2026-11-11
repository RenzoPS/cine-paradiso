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


def _motivo_del_error(respuesta):
    try:
        return respuesta.json()['errors'][0]['description']
    except (ValueError, KeyError, IndexError):
        return MOTIVO_POR_DEFECTO