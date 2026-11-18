import base64

import requests

from cine_paradiso_web.constants import API_TIMEOUT_SEGUNDOS, API_URL, TOKEN_COOKIE_NOMBRE

MOTIVO_POR_DEFECTO = 'No pudimos confirmar tu compra. Intentá de nuevo en unos minutos'
MOTIVO_LISTADO_POR_DEFECTO = 'No pudimos cargar tus entradas. Intentá de nuevo en unos minutos'


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


def listar_compras_usuario(token, limit=50, offset=0):
    """
    Pide a la API el listado paginado de compras del cliente autenticado.
    Devuelve (compras, None) si salió bien o ([], motivo) si falló.
    """
    try:
        respuesta = requests.get(
            f'{API_URL}/compras',
            params={'_limit': limit, '_offset': offset},
            cookies={TOKEN_COOKIE_NOMBRE: token},
            timeout=API_TIMEOUT_SEGUNDOS,
        )
    except requests.RequestException:
        return [], MOTIVO_LISTADO_POR_DEFECTO

    if respuesta.ok:
        return respuesta.json().get('compras', []), None
    return [], _motivo_del_error(respuesta, MOTIVO_LISTADO_POR_DEFECTO)


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


def _motivo_del_error(respuesta, por_defecto=MOTIVO_POR_DEFECTO):
    try:
        return respuesta.json()['errors'][0]['description']
    except (ValueError, KeyError, IndexError):
        return por_defecto