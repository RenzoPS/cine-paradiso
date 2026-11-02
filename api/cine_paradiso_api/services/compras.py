import logging
from datetime import datetime
from decimal import Decimal
from io import BytesIO

from ..constants import (
    ERROR_CODE_COMPRA_NO_CONFIRMABLE,
    ERROR_CODE_COMPRA_NOT_FOUND,
    ERROR_CODE_COMPRA_SIN_FACTURA,
    ERROR_CODE_COMPRA_VENCIDA,
    ERROR_CODE_QR_CANCELADO,
    ERROR_CODE_QR_NO_PAGADO,
    ERROR_CODE_QR_OTRA_FUNCION,
    ERROR_CODE_QR_OTRO_DIA,
    ERROR_CODE_QR_SIN_EMITIR,
    ERROR_CODE_QR_UTILIZADO,
    ESTADO_CANCELADA,
    ESTADO_PAGADA,
    ESTADO_PENDIENTE,
    ESTADO_USADA,
    ESTADO_VENCIDA,
    HORAS_LIMITE_CANCELACION,
    TZ_ARG,
    WEB_URL,
)
from ..repositories import compras as db_compras
from ..utils import ErrorAPI, formatear_fecha_hora
from ..validators.compras import validar_cuerpo_validacion_qr, validar_id_compra
from . import mail as mail_service
from .mail_plantillas import CONFIRMACION_COMPRA
from .qr import error_qr_invalido, generar_imagen_qr, generar_token_qr, leer_token_qr

ESTADOS_CON_QR = (ESTADO_PAGADA, ESTADO_USADA)

logger = logging.getLogger(__name__)

def _ahora() -> datetime:
    return datetime.now(TZ_ARG).replace(tzinfo=None)


def _obtener_compra_propia(id_compra: int, id_usuario: int) -> dict:
    """
    Busca la compra y si no existe o es de otro usuario da error, responde 404.
    """
    compra = db_compras.obtener_compra_por_id(id_compra)

    if not compra or compra['fk_id_usuario'] != id_usuario:
        raise ErrorAPI(
            code=ERROR_CODE_COMPRA_NOT_FOUND,
            message='Compra no encontrada',
            description=f"No existe una compra con id '{id_compra}'",
            status=404,
        )
    return compra

def _validar_compra_confirmable(compra: dict) -> None:
    """
    La compra solo se confirma si esta pendiente y su reserva no vencio.
    """
    vencio_por_tiempo = (
        compra['estado'] == ESTADO_PENDIENTE
        and compra['fecha_vencimiento'] is not None
        and compra['fecha_vencimiento'] <= _ahora()
    )
    if compra['estado'] == ESTADO_VENCIDA or vencio_por_tiempo:
        raise ErrorAPI(
            code=ERROR_CODE_COMPRA_VENCIDA,
            message='La reserva vencio',
            description='El tiempo de la reserva termino. Volve a elegir tus butacas',
            status=409,
        )
    if compra['estado'] != ESTADO_PENDIENTE:
        raise ErrorAPI(
            code=ERROR_CODE_COMPRA_NO_CONFIRMABLE,
            message='La compra no se puede confirmar',
            description=f"La compra esta en estado '{compra['estado']}' y solo se confirman las pendientes",
            status=409,
        )

def _generar_numero_factura(id_compra: int) -> str:
    """
    Agrega al id de la compra los 0 necesarios a la izquierda hasta lograr 8 digitos en el numero de factura
    """
    return f'{id_compra:08d}'

def _armar_factura(compra: dict) -> dict:
    """
    Arma la factura de la compra: entradas, servicios y subtotales.
    """
    entradas = db_compras.obtener_entradas_de_compra(compra['id_compra'])
    servicios = db_compras.obtener_servicios_de_compra(compra['id_compra'])

    lista_entradas = []
    subtotal_entradas = Decimal('0')
    for entrada in entradas:
        subtotal_entradas += entrada['precio_unitario']
        lista_entradas.append({
            'fila': entrada['fila'],
            'numero': entrada['numero'],
            'precio_unitario': str(entrada['precio_unitario']),
        })

    lista_servicios = []
    subtotal_servicios = Decimal('0')
    for servicio in servicios:
        subtotal = servicio['cantidad'] * servicio['precio_unitario']
        subtotal_servicios += subtotal
        lista_servicios.append({
            'nombre': servicio['nombre'],
            'cantidad': servicio['cantidad'],
            'precio_unitario': str(servicio['precio_unitario']),
            'subtotal': str(subtotal),
        })

    return {
        'id_compra': compra['id_compra'],
        'numero_factura': compra['numero_factura'],
        'estado': compra['estado'],
        'fecha_pago': formatear_fecha_hora(compra['fecha_pago']),
        'entradas': lista_entradas,
        'servicios': lista_servicios,
        'subtotal_entradas': str(subtotal_entradas),
        'subtotal_servicios': str(subtotal_servicios),
        'total': str(compra['total']),
        'mail_enviado': None,
    }

def _texto_butacas(entradas: list[dict]) -> str:
    """
    Agrupa las entradas por fila: 'Fila E - asientos 8, 9'.
    """
    numeros_por_fila = {}

    for entrada in entradas:
        numeros_por_fila.setdefault(entrada['fila'], []).append(entrada['numero'])

    partes = []
    for fila, numeros in numeros_por_fila.items():
        palabra = 'asiento' if len(numeros) == 1 else 'asientos'
        numeros_texto = ', '.join(str(n) for n in numeros)
        partes.append(f'Fila {fila} - {palabra} {numeros_texto}')

    return ' / '.join(partes)

def _enviar_mail_confirmacion(compra: dict, factura: dict) -> bool:
    """
    Manda el mail de confirmacion. Devuelve False si falla: la compra ya quedo pagada y no se deshace.
    """
    try:
        datos = db_compras.obtener_datos_para_mail(compra['id_compra'])

        cuerpo_mail = mail_service.armar_mail(CONFIRMACION_COMPRA, {
            'pelicula': datos['titulo'],
            'sala': datos['sala'],
            'fecha_hora': datos['fecha_hora'].strftime('%d/%m/%Y %H:%M'),
            'butacas': _texto_butacas(factura['entradas']),
            'cantidad_entradas': len(factura['entradas']),
            'total_entradas': factura['subtotal_entradas'],
            'total_servicios': factura['subtotal_servicios'],
            'total': factura['total'],
            'numero_factura': factura['numero_factura'],
            'link_cancelar': f"{WEB_URL}/compras/{compra['id_compra']}/cancelar",
            'horas_limite': HORAS_LIMITE_CANCELACION,
        })

        return mail_service.enviar_mail(
            datos['email'],
            f"Compra en Cine Paradiso - Factura N° {factura ['numero_factura']}",
            cuerpo_mail,
            generar_qr_de_compra(compra['id_compra']).getvalue(),
        )
    except Exception:
        logger.exception('No se pudo armar el mail de la compra %s', compra['id_compra'])

        return False


def confirmar_compra(id_compra, id_usuario: int) -> dict:
    """
    Pasa la compra de pendiente a pagada, genera la factura y manda el mail. Si ya estaba pagada devuelve la misma factura sin facturar de nuevo.
    """
    id_validado = validar_id_compra(id_compra)
    compra = _obtener_compra_propia(id_validado, id_usuario)

    if compra['estado'] == ESTADO_PAGADA:
        return _armar_factura(compra)

    _validar_compra_confirmable(compra)
    numero_factura = _generar_numero_factura(id_validado)
    pagada_ahora = db_compras.actualizar_compra_pagada(id_validado, numero_factura, _ahora())

    compra = db_compras.obtener_compra_por_id(id_validado)
    factura = _armar_factura(compra)

    if pagada_ahora:
        factura['mail_enviado'] = _enviar_mail_confirmacion(compra, factura)
    return factura
    


def obtener_factura(id_compra, id_usuario: int) -> dict:
    """
    Datos de la factura de una compra que ya esta pagada.
    """
    id_validado = validar_id_compra(id_compra)
    compra = _obtener_compra_propia(id_validado, id_usuario)

    if not compra['numero_factura']:
        raise ErrorAPI(
            code=ERROR_CODE_COMPRA_SIN_FACTURA,
            message='La compra no tiene factura',
            description=f"La compra '{id_validado}' todavia no fue pagada",
            status=409,
        )
    return _armar_factura(compra)


def _rechazar_ingreso(code: str, message: str, description: str) -> ErrorAPI:
    return ErrorAPI(code=code, message=message, description=description, status=409)


def _error_qr_utilizado(compra: dict) -> ErrorAPI:
    return _rechazar_ingreso(
        ERROR_CODE_QR_UTILIZADO,
        'QR ya utilizado',
        f"El QR ya fue validado el {formatear_fecha_hora(compra['fecha_validacion'])}",
    )


def generar_qr_de_compra(id_compra: int) -> BytesIO:
    """
    Imagen PNG del QR de una compra pagada. Genera y guarda el token la primera vez.
    """
    compra = db_compras.obtener_compra_por_id(id_compra)

    if compra.get('estado') not in ESTADOS_CON_QR:
        raise _rechazar_ingreso(
            ERROR_CODE_QR_SIN_EMITIR,
            'La compra no tiene QR',
            f"El QR se genera cuando la compra esta pagada. Estado actual: '{compra.get('estado')}'",
        )

    if compra['qr_token'] is None:
        compra['qr_token'] = generar_token_qr(id_compra)
        db_compras.guardar_qr_token(id_compra, compra['qr_token'])

    return generar_imagen_qr(compra['qr_token'])


def obtener_qr_de_compra(id_compra, id_usuario: int) -> BytesIO:
    """
    QR de una compra del usuario logueado.
    """
    id_validado = validar_id_compra(id_compra)
    _obtener_compra_propia(id_validado, id_usuario)
    return generar_qr_de_compra(id_validado)


def validar_ingreso(body) -> dict:
    """
    Valida el QR en la puerta de la sala: tiene que ser de esa funcion y de hoy, y no estar usado ni cancelado.
    """
    qr_token, id_funcion = validar_cuerpo_validacion_qr(body)
    compra = db_compras.obtener_compra_por_id(leer_token_qr(qr_token))

    if not compra or compra['qr_token'] != qr_token:
        raise error_qr_invalido()

    if compra['estado'] == ESTADO_USADA:
        raise _error_qr_utilizado(compra)

    if compra['estado'] == ESTADO_CANCELADA:
        raise _rechazar_ingreso(ERROR_CODE_QR_CANCELADO, 'QR cancelado', 'La compra fue cancelada')

    if compra['estado'] != ESTADO_PAGADA:
        raise _rechazar_ingreso(ERROR_CODE_QR_NO_PAGADO, 'Compra sin pagar', f"Estado de la compra: '{compra['estado']}'")

    if compra['fk_id_funcion'] != id_funcion:
        raise _rechazar_ingreso(ERROR_CODE_QR_OTRA_FUNCION, 'QR de otra funcion', 'El QR corresponde a otra funcion')

    fecha_hora_funcion = db_compras.obtener_fecha_hora_funcion(id_funcion)
    ahora = _ahora()

    if fecha_hora_funcion.date() != ahora.date():
        raise _rechazar_ingreso(
            ERROR_CODE_QR_OTRO_DIA,
            'QR de otro dia',
            f'La funcion es el {formatear_fecha_hora(fecha_hora_funcion)}',
        )

    if not db_compras.marcar_compra_usada(compra['id_compra'], ahora):
        raise _error_qr_utilizado(db_compras.obtener_compra_por_id(compra['id_compra']))

    entradas = db_compras.obtener_entradas_de_compra(compra['id_compra'])
    return {
        'id_compra': compra['id_compra'],
        'estado': ESTADO_USADA,
        'fecha_validacion': formatear_fecha_hora(ahora),
        'butacas': [f"{entrada['fila']}{entrada['numero']}" for entrada in entradas],
    }
