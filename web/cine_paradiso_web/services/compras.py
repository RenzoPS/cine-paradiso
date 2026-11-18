from cine_paradiso_web.services.api_service import ApiError, llamar_api


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


def obtener_compra(id_compra):
    """
    Pide a la API los datos de la compra.
    """
    try:
        compra = llamar_api('GET', f'/compras/{id_compra}')
    except ApiError as error:
        return None, error.mensaje
    return compra, None
