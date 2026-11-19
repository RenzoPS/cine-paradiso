from decimal import Decimal, InvalidOperation

from ..constants import ERROR_CODE_INVALID_FORMAT, ERROR_CODE_INVALID_MAX_VALUE
from ..paginacion import PARAMETROS_PAGINACION
from ..utils import (
    ErrorAPI,
    rechazar_campos_desconocidos,
    validar_booleano,
    validar_cuerpo_no_vacio,
    validar_entero_positivo,
    validar_maximo,
    validar_minimo,
    validar_string_no_vacio,
)

CAMPOS_SERVICIO = {'nombre', 'descripcion', 'precio', 'activo'}
CAMPOS_ITEM_COMPRA = {'id_servicio', 'cantidad'}

NOMBRE_MAX = 80
DESCRIPCION_MAX = 255
PRECIO_MIN = Decimal('0')
PRECIO_MAX = Decimal('99999999.99')
MAX_UNIDADES_POR_SERVICIO = 20


def validar_id_servicio(id_servicio) -> int:
    return validar_entero_positivo(id_servicio, 'id_servicio')


def _validar_largo(texto: str, nombre: str, maximo: int) -> str:
    if len(texto) > maximo:
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_MAX_VALUE,
            message='Texto demasiado largo',
            description=f"El campo '{nombre}' admite hasta {maximo} caracteres. Se recibio: {len(texto)}"
        )

    return texto


def _validar_descripcion(valor) -> str | None:
    descripcion = None

    if isinstance(valor, str) and valor.strip():
        descripcion = _validar_largo(valor.strip(), 'descripcion', DESCRIPCION_MAX)
    elif valor is not None and not isinstance(valor, str):
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_FORMAT,
            message="Formato de 'descripcion' invalido",
            description="El campo 'descripcion' debe ser un texto"
        )

    return descripcion


def _validar_precio(valor) -> Decimal:
    try:
        if isinstance(valor, bool):
            raise InvalidOperation

        precio = Decimal(str(valor).strip())

        if not precio.is_finite():
            raise InvalidOperation
    except InvalidOperation:
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_FORMAT,
            message="Formato de 'precio' invalido",
            description=f"El valor '{valor}' no es un numero valido para 'precio'"
        )

    validar_minimo(precio, PRECIO_MIN, 'precio')
    validar_maximo(precio, PRECIO_MAX, 'precio')

    return precio.quantize(Decimal('0.01'))


def validar_cuerpo_servicio(body) -> dict:
    datos = validar_cuerpo_no_vacio(body)
    rechazar_campos_desconocidos(datos, CAMPOS_SERVICIO)

    return {
        'nombre': _validar_largo(validar_string_no_vacio(datos.get('nombre'), 'nombre'), 'nombre', NOMBRE_MAX),
        'descripcion': _validar_descripcion(datos.get('descripcion')),
        'precio': _validar_precio(datos.get('precio')),
        'activo': validar_booleano(datos.get('activo', True), 'activo'),
    }


def validar_parametros_listado_servicios(args) -> bool:
    """Por defecto solo se listan los servicios activos; `activo=false` lista los dados de baja."""
    rechazar_campos_desconocidos(args, PARAMETROS_PAGINACION | {'activo'}, 'query string')

    return validar_booleano(args.get('activo', 'true'), 'activo')


def validar_cuerpo_servicios_de_compra(body) -> list[dict]:
    datos = validar_cuerpo_no_vacio(body)
    rechazar_campos_desconocidos(datos, {'servicios'})

    items = datos.get('servicios')

    if not isinstance(items, list):
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_FORMAT,
            message="Formato de 'servicios' invalido",
            description="El campo 'servicios' debe ser una lista de objetos con 'id_servicio' y 'cantidad'"
        )

    validados = []
    repetidos = set()

    for item in items:
        item = validar_cuerpo_no_vacio(item, 'servicio')
        rechazar_campos_desconocidos(item, CAMPOS_ITEM_COMPRA, 'servicio')

        id_servicio = validar_id_servicio(item.get('id_servicio'))
        cantidad = validar_maximo(
            validar_entero_positivo(item.get('cantidad'), 'cantidad'),
            MAX_UNIDADES_POR_SERVICIO,
            'cantidad',
        )

        if id_servicio in repetidos:
            raise ErrorAPI(
                code=ERROR_CODE_INVALID_FORMAT,
                message='Servicios repetidos',
                description=f"El servicio {id_servicio} aparece mas de una vez en la solicitud"
            )

        repetidos.add(id_servicio)
        validados.append({'id_servicio': id_servicio, 'cantidad': cantidad})

    return validados
