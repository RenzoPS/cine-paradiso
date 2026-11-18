import logging
from datetime import datetime, timedelta
from decimal import Decimal
from io import BytesIO

from sqlalchemy.exc import IntegrityError

from ..constants import (
    ERROR_CODE_COMPRA_BUTACA_AJENA,
    ERROR_CODE_COMPRA_BUTACA_OCUPADA,
    ERROR_CODE_COMPRA_FUNCION_PASADA,
    ERROR_CODE_COMPRA_NO_ABANDONABLE,
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
    MINUTOS_RESERVA,
    TZ_ARG,
    WEB_URL,
)
from ..repositories import compras as db_compras
from ..repositories import transaccion
from ..utils import ErrorAPI, formatear_fecha_hora
from ..validators.compras import validar_cuerpo_compra, validar_cuerpo_validacion_qr, validar_id_compra
from .funciones import buscar_funcion
from . import mail as mail_service
from .mail_plantillas import CONFIRMACION_COMPRA
from .qr import error_qr_invalido, generar_imagen_qr, generar_token_qr, leer_token_qr

ESTADOS_CON_QR = (ESTADO_PAGADA, ESTADO_USADA)
ESTADOS_CON_FACTURA = (ESTADO_PAGADA, ESTADO_USADA, ESTADO_CANCELADA)

logger = logging.getLogger(__name__)

def _ahora() -> datetime:
    return datetime.now(TZ_ARG).replace(tzinfo=None)


def _limite_reserva() -> datetime:
    """
    Las compras pendientes creadas antes de este momento ya vencieron.
    """
    return _ahora() - timedelta(minutes=MINUTOS_RESERVA)


def vencer_reservas_de_funcion(id_funcion: int) -> None:
    """
    Vencimiento lazy del hold: antes de mirar una funcion se vencen sus compras
    pendientes que superaron el tiempo de reserva y se liberan sus butacas.
    Bloquea la funcion igual que la reserva, asi no se cruzan en un deadlock.
    """
    with transaccion() as conexion:
        db_compras.bloquear_funcion(conexion, id_funcion)
        db_compras.liberar_reservas_vencidas(conexion, id_funcion, _limite_reserva())


def _obtener_compra_propia(id_compra: int, id_usuario: int) -> dict:
    """
    Busca la compra y si no existe o es de otro usuario responde 404.
    Si esta pendiente, primero vence los holds de su funcion para devolver el estado real.
    """
    compra = db_compras.obtener_compra_por_id(id_compra)

    if not compra or compra['fk_id_usuario'] != id_usuario:
        raise _error_compra_no_encontrada(id_compra)

    if compra['estado'] == ESTADO_PENDIENTE:
        vencer_reservas_de_funcion(compra['fk_id_funcion'])
        compra = db_compras.obtener_compra_por_id(id_compra)

    return compra


def _error_compra_no_encontrada(id_compra: int) -> ErrorAPI:
    return ErrorAPI(
        code=ERROR_CODE_COMPRA_NOT_FOUND,
        message='Compra no encontrada',
        description=f"No existe una compra con id '{id_compra}'",
        status=404,
    )

def _validar_compra_confirmable(compra: dict) -> None:
    """
    La compra solo se confirma si esta pendiente y su reserva no vencio.
    """
    if compra['estado'] == ESTADO_VENCIDA:
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
    datos_funcion = db_compras.obtener_datos_para_mail(compra['id_compra'])

    lista_entradas = []
    subtotal_entradas = Decimal('0')
    for entrada in entradas:
        subtotal_entradas += datos_funcion['precio']
        lista_entradas.append({
            'fila': entrada['fila'],
            'numero': entrada['numero'],
            'precio_unitario': str(datos_funcion['precio']),
        })

    lista_servicios = []
    subtotal_servicios = Decimal('0')
    for servicio in servicios:
        subtotal = servicio['cantidad'] * servicio['precio']
        subtotal_servicios += subtotal
        lista_servicios.append({
            'nombre': servicio['nombre'],
            'cantidad': servicio['cantidad'],
            'precio_unitario': str(servicio['precio']),
            'subtotal': str(subtotal),
        })

    return {
        'id_compra': compra['id_compra'],
        'numero_factura': _generar_numero_factura(compra['id_compra']),
        'estado': compra['estado'],
        'funcion': {
            'pelicula': datos_funcion['titulo'],
            'sala': datos_funcion['sala'],
            'fecha_hora': datos_funcion['fecha_hora'].strftime('%d/%m/%Y %H:%M'),
        },
        'entradas': lista_entradas,
        'servicios': lista_servicios,
        'subtotal_entradas': str(subtotal_entradas),
        'subtotal_servicios': str(subtotal_servicios),
        'total': str(subtotal_entradas + subtotal_servicios),
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
            'pelicula': factura['funcion']['pelicula'],
            'sala': factura['funcion']['sala'],
            'fecha_hora': factura['funcion']['fecha_hora'],
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
    pagada_ahora = db_compras.actualizar_compra_pagada(id_validado)

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

    if compra['estado'] not in ESTADOS_CON_FACTURA:
        raise ErrorAPI(
            code=ERROR_CODE_COMPRA_SIN_FACTURA,
            message='La compra no tiene factura',
            description=f"La compra '{id_validado}' todavia no fue pagada",
            status=409,
        )
    return _armar_factura(compra)


def _rechazar_ingreso(code: str, message: str, description: str) -> ErrorAPI:
    return ErrorAPI(code=code, message=message, description=description, status=409)


def _error_qr_utilizado() -> ErrorAPI:
    return _rechazar_ingreso(
        ERROR_CODE_QR_UTILIZADO,
        'QR ya utilizado',
        'El QR ya fue validado anteriormente'
    )


def generar_qr_de_compra(id_compra: int) -> BytesIO:
    """
    Imagen PNG del QR de una compra pagada.  El QR se genera de nuevo cada vez, no se guarda
    """
    compra = db_compras.obtener_compra_por_id(id_compra)

    if compra:
        estado = compra['estado']
    else:
        estado = None
    
    if estado not in ESTADOS_CON_QR:
        raise _rechazar_ingreso(
            ERROR_CODE_QR_SIN_EMITIR,
            'La compra no tiene QR',
            f"El QR se genera cuando la compra esta pagada. Estado actual: '{estado}'",
        )

    return generar_imagen_qr(generar_token_qr(id_compra))


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

    if not compra :
        raise error_qr_invalido()

    if compra['estado'] == ESTADO_USADA:
        raise _error_qr_utilizado()

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

    if not db_compras.marcar_compra_usada(compra['id_compra']):
        raise _error_qr_utilizado()

    entradas = db_compras.obtener_entradas_de_compra(compra['id_compra'])
    return {
        'id_compra': compra['id_compra'],
        'estado': ESTADO_USADA,
        'fecha_validacion': formatear_fecha_hora(ahora),
        'butacas': [f"{entrada['fila']}{entrada['numero']}" for entrada in entradas],
    }


def crear_compra(body, id_usuario: int) -> dict:
    """
    Reserva las butacas: crea la compra pendiente y sus entradas en una sola transaccion.
    Si otra compra tomo alguna butaca, el UNIQUE de entradas lo frena y responde 409.
    """
    id_funcion, butacas = validar_cuerpo_compra(body)
    funcion = buscar_funcion(id_funcion)
    ahora = _ahora()

    try:
        with transaccion() as conexion:
            if db_compras.bloquear_funcion(conexion, id_funcion) <= ahora:
                raise ErrorAPI(
                    code=ERROR_CODE_COMPRA_FUNCION_PASADA,
                    message='La funcion ya comenzo',
                    description='Solo se pueden reservar butacas de funciones futuras',
                    status=409,
                )
            if db_compras.contar_butacas_de_sala(conexion, funcion['id_sala'], butacas) != len(butacas):
                raise ErrorAPI(
                    code=ERROR_CODE_COMPRA_BUTACA_AJENA,
                    message='Butaca invalida',
                    description='Alguna de las butacas no pertenece a la sala de la funcion',
                )

            db_compras.liberar_reservas_vencidas(conexion, id_funcion, _limite_reserva())
            id_compra = db_compras.insertar_compra(conexion, id_usuario, id_funcion, ahora)
            db_compras.insertar_entradas(conexion, id_compra, id_funcion, butacas)
    except IntegrityError as error:
        raise ErrorAPI(
            code=ERROR_CODE_COMPRA_BUTACA_OCUPADA,
            message='Butaca ocupada',
            description='Alguna de las butacas elegidas ya fue reservada. Volve a elegir',
            status=409,
        ) from error

    return buscar_compra(id_compra, id_usuario)


def buscar_compra(id_compra, id_usuario: int) -> dict:
    id_validado = validar_id_compra(id_compra)
    compra = _obtener_compra_propia(id_validado, id_usuario)

    funcion = buscar_funcion(compra['fk_id_funcion'])
    butacas = db_compras.obtener_entradas_de_compra(id_validado)

    vence_en = None
    if compra['estado'] == ESTADO_PENDIENTE:
        vence_en = compra['fecha_hora'] + timedelta(minutes=MINUTOS_RESERVA)

    return {
        'id_compra': compra['id_compra'],
        'estado': compra['estado'],
        'fecha_hora': formatear_fecha_hora(compra['fecha_hora']),
        'vence_en': formatear_fecha_hora(vence_en),
        'funcion': funcion,
        'butacas': butacas,
        'subtotal_entradas': str(Decimal(funcion['precio']) * len(butacas)),
    }


def abandonar_compra(id_compra, id_usuario: int) -> None:
    """
    Cancelar antes de pagar: borra la compra con sus entradas y servicios, asi las
    butacas quedan libres y no cuenta como cancelacion en los dashboards.
    """
    id_validado = validar_id_compra(id_compra)
    with transaccion() as conexion:
        compra = db_compras.bloquear_compra(conexion, id_validado)
        if compra is None or compra['fk_id_usuario'] != id_usuario:
            raise _error_compra_no_encontrada(id_validado)

        if compra['estado'] != ESTADO_PENDIENTE:
            raise ErrorAPI(
                code=ERROR_CODE_COMPRA_NO_ABANDONABLE,
                message='La compra no se puede abandonar',
                description=f"La compra esta en estado '{compra['estado']}' y solo se abandonan las pendientes",
                status=409,
            )

        db_compras.eliminar_compra(conexion, id_validado)
