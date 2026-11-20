import base64
from datetime import datetime

import requests

from cine_paradiso_web.constants import API_TIMEOUT_SEGUNDOS, API_URL, TOKEN_COOKIE_NOMBRE, TZ_ARG
from cine_paradiso_web.services.api_service import ApiError, llamar_api

MOTIVO_POR_DEFECTO = 'No pudimos confirmar tu compra. Intentá de nuevo en unos minutos'
MOTIVO_LISTADO_POR_DEFECTO = 'No pudimos cargar tus entradas. Intentá de nuevo en unos minutos'


def confirmar_compra(id_compra):
    """
    Pide a la API que confirme la compra.
    """
    try:
        factura = llamar_api('POST', f'/compras/{id_compra}/confirmar')
    except ApiError as error:
        return None, error.mensaje
    return factura, None


def cancelar_compra(id_compra):
    """
    Pide a la API que cancele la compra.
    """
    try:
        llamar_api('POST', f'/compras/{id_compra}/cancelar')
    except ApiError as error:
        return False, error.mensaje
    return True, None


def abandonar_compra(id_compra):
    """
    Pide a la API que borre una compra que todavía no se pagó.
    """
    try:
        llamar_api('DELETE', f'/compras/{id_compra}')
    except ApiError as error:
        return False, error.mensaje
    return True, None


def segundos_para_vencer(compra: dict) -> int:
    """
    Segundos que le quedan a la reserva de una compra pendiente, para la cuenta regresiva.
    """
    vence_en = datetime.fromisoformat(compra['vence_en'])

    return max(0, int((vence_en - datetime.now(TZ_ARG)).total_seconds()))


def obtener_compra(id_compra):
    """
    Pide a la API los datos de la compra.
    """
    try:
        compra = llamar_api('GET', f'/compras/{id_compra}')
    except ApiError as error:
        return None, error.mensaje
    return compra, None


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


def validar_ingreso_qr(qr_token):
    return llamar_api(
        'POST',
        'compras/validar',
        json={'qr_token': qr_token},
    )


def listar_compras_validacion_admin():
    return llamar_api('GET', 'compras/admin')


def validar_ingreso_por_id_compra(id_compra):
    return llamar_api('POST', f'compras/{id_compra}/validar')


def _motivo_del_error(respuesta, por_defecto=MOTIVO_POR_DEFECTO):
    try:
        return respuesta.json()['errors'][0]['description']
    except (ValueError, KeyError, IndexError):
        return por_defecto
