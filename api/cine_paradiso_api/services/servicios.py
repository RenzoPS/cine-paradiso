from ..constants import BASE_URL, ERROR_CODE_NOT_FOUND
from ..paginacion import leer_parametros_paginacion, paginar
from ..repositories import servicios as repositorio
from ..utils import ErrorAPI
from ..validators.servicios import leer_filtro_activo, validar_estado, validar_servicio

PATH_SERVICIOS = f'{BASE_URL}/servicios'


def _serializar(fila: dict) -> dict:
    return {
        'id': fila['id'],
        'nombre': fila['nombre'],
        'descripcion': fila['descripcion'],
        'precio': float(fila['precio']),
        'imagen_url': fila['imagen_url'],
        'activo': bool(fila['activo']),
    }


def _obtener_existente(servicio_id: int) -> dict:
    fila = repositorio.obtener_por_id(servicio_id)

    if fila is None:
        raise ErrorAPI(
            code=ERROR_CODE_NOT_FOUND,
            message='Servicio no encontrado',
            description=f'No existe un servicio con id {servicio_id}',
            status=404
        )

    return fila


def listar(args) -> dict:
    activo = leer_filtro_activo(args)
    limit, offset = leer_parametros_paginacion(args)

    filas, total = repositorio.listar(activo, limit, offset)

    return paginar([_serializar(fila) for fila in filas], total, limit, offset,
                   'servicios', PATH_SERVICIOS, {'activo': activo})


def obtener(servicio_id: int) -> dict:
    return _serializar(_obtener_existente(servicio_id))


def crear(body) -> dict:
    nuevo_id = repositorio.crear(validar_servicio(body))

    return obtener(nuevo_id)


def modificar(servicio_id: int, body) -> dict:
    _obtener_existente(servicio_id)
    repositorio.actualizar(servicio_id, validar_servicio(body))

    return obtener(servicio_id)


def cambiar_estado(servicio_id: int, body) -> dict:
    _obtener_existente(servicio_id)
    repositorio.cambiar_estado(servicio_id, validar_estado(body))

    return obtener(servicio_id)


def dar_de_baja(servicio_id: int) -> None:
    """Baja logica: deja de ofrecerse, pero queda en el historial de compras."""
    _obtener_existente(servicio_id)
    repositorio.cambiar_estado(servicio_id, False)
