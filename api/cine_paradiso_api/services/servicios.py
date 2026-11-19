from decimal import Decimal

from ..constants import BASE_URL, ERROR_CODE_COMPRA_NOT_FOUND, ESTADO_PENDIENTE
from ..paginacion import leer_parametros_paginacion, paginar
from ..repositories import transaccion
from ..repositories.compras import bloquear_compra, obtener_servicios_de_compra
from ..repositories.servicios import (
    actualizar_servicio as guardar_actualizacion,
    desactivar_servicio as dar_baja_servicio,
    insertar_servicio as guardar_servicio,
    listar_servicios as consultar_servicios,
    obtener_servicio_por_id,
    reemplazar_servicios_de_compra as guardar_servicios_de_compra,
)
from ..services.compras import _obtener_compra_propia
from ..utils import ErrorAPI
from ..validators.compras import validar_id_compra
from ..validators.servicios import (
    validar_cuerpo_servicio,
    validar_cuerpo_servicios_de_compra,
    validar_id_servicio,
    validar_parametros_listado_servicios,
)

PATH_SERVICIOS = f'{BASE_URL}/servicios'


def _formatear_servicio(servicio: dict) -> dict:
    return {
        'id_servicio': servicio['id_servicio'],
        'nombre': servicio['nombre'],
        'descripcion': servicio['descripcion'],
        'precio': str(servicio['precio']),
        'activo': bool(servicio['activo']),
    }


def _error_servicio_no_encontrado(id_servicio: int) -> ErrorAPI:
    return ErrorAPI(
        code='servicio.not.found',
        message='Servicio no encontrado',
        description=f'No existe un servicio con id {id_servicio}',
        status=404,
    )


def _error_servicio_no_disponible(id_servicio: int) -> ErrorAPI:
    return ErrorAPI(
        code='servicio.not.available',
        message='Servicio no disponible',
        description=f'El servicio {id_servicio} no existe o esta dado de baja',
        status=409,
    )


def _error_compra_no_modificable(estado: str) -> ErrorAPI:
    return ErrorAPI(
        code='compra.no.modificable',
        message='La compra no admite cambios',
        description=f"Solo se pueden modificar los servicios de una compra pendiente. Estado actual: '{estado}'",
        status=409,
    )


def _obtener_servicio_existente(id_servicio: int) -> dict:
    servicio = obtener_servicio_por_id(id_servicio)

    if servicio is None:
        raise _error_servicio_no_encontrado(id_servicio)

    return servicio


def listar_servicios(args) -> dict:
    activo = validar_parametros_listado_servicios(args)
    limit, offset = leer_parametros_paginacion(args)

    filas, total = consultar_servicios(activo, limit, offset)

    return paginar(
        [_formatear_servicio(fila) for fila in filas],
        total, limit, offset,
        'servicios', PATH_SERVICIOS, {'activo': activo},
    )


def buscar_servicio(id_servicio) -> dict:
    id_validado = validar_id_servicio(id_servicio)

    return _formatear_servicio(_obtener_servicio_existente(id_validado))


def crear_servicio(body) -> dict:
    datos = validar_cuerpo_servicio(body)
    id_servicio = guardar_servicio(datos)

    return _formatear_servicio(_obtener_servicio_existente(id_servicio))


def actualizar_servicio(id_servicio, body) -> dict:
    id_validado = validar_id_servicio(id_servicio)
    _obtener_servicio_existente(id_validado)

    guardar_actualizacion(id_validado, validar_cuerpo_servicio(body))

    return _formatear_servicio(_obtener_servicio_existente(id_validado))


def eliminar_servicio(id_servicio) -> dict:
    """Baja logica: el servicio deja de ofrecerse, pero las compras anteriores lo conservan."""
    id_validado = validar_id_servicio(id_servicio)
    _obtener_servicio_existente(id_validado)

    dar_baja_servicio(id_validado)

    return _formatear_servicio(_obtener_servicio_existente(id_validado))


def _armar_servicios_de_compra(id_compra: int) -> dict:
    lineas = []
    subtotal = Decimal('0')

    for servicio in obtener_servicios_de_compra(id_compra):
        subtotal_linea = servicio['cantidad'] * servicio['precio']
        subtotal += subtotal_linea
        lineas.append({
            'id_servicio': servicio['id_servicio'],
            'nombre': servicio['nombre'],
            'cantidad': servicio['cantidad'],
            'precio_unitario': str(servicio['precio']),
            'subtotal': str(subtotal_linea),
        })

    return {'id_compra': id_compra, 'servicios': lineas, 'subtotal_servicios': str(subtotal)}


def buscar_servicios_de_compra(id_compra, id_usuario: int) -> dict:
    compra = _obtener_compra_propia(validar_id_compra(id_compra), id_usuario)

    return _armar_servicios_de_compra(compra['id_compra'])


def definir_servicios_de_compra(id_compra, body, id_usuario: int) -> dict:
    id_validado = validar_id_compra(id_compra)
    items = validar_cuerpo_servicios_de_compra(body)
    compra = _obtener_compra_propia(id_validado, id_usuario)

    if compra['estado'] != ESTADO_PENDIENTE:
        raise _error_compra_no_modificable(compra['estado'])

    with transaccion() as conexion:
        compra_bloqueada = bloquear_compra(conexion, compra['id_compra'])

        if compra_bloqueada is None:
            raise ErrorAPI(
                code=ERROR_CODE_COMPRA_NOT_FOUND,
                message='Compra no encontrada',
                description=f"No existe una compra con id '{id_validado}'",
                status=404,
            )

        if compra_bloqueada['estado'] != ESTADO_PENDIENTE:
            raise _error_compra_no_modificable(compra_bloqueada['estado'])

        servicio_no_disponible = guardar_servicios_de_compra(conexion, compra['id_compra'], items)

        if servicio_no_disponible is not None:
            # Al salir con error la transaccion se revierte y la compra queda como estaba.
            raise _error_servicio_no_disponible(servicio_no_disponible)

    return _armar_servicios_de_compra(compra['id_compra'])
