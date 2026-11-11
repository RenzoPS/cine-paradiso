from decimal import Decimal, InvalidOperation

from ..constants import ERROR_CODE_INVALID_FORMAT, ERROR_CODE_INVALID_MAX_VALUE
from ..paginacion import PARAMETROS_PAGINACION
from ..utils import (
    ErrorAPI,
    rechazar_campos_desconocidos,
    validar_booleano,
    validar_cuerpo_no_vacio,
    validar_maximo,
    validar_minimo,
    validar_string_no_vacio,
)

CAMPOS_SERVICIO = {'nombre', 'descripcion', 'precio', 'imagen_url', 'activo'}

NOMBRE_MAX = 100
TEXTO_MAX = 255
PRECIO_MIN = Decimal('0.01')
PRECIO_MAX = Decimal('99999999.99')


def _validar_largo(texto: str, nombre: str, maximo: int) -> str:
    if len(texto) > maximo:
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_MAX_VALUE,
            message='Texto demasiado largo',
            description=f"El campo '{nombre}' admite hasta {maximo} caracteres. Se recibio: {len(texto)}"
        )

    return texto


def _texto_opcional(valor, nombre: str, maximo: int) -> str | None:
    texto = None
    es_vacio = valor is None or (isinstance(valor, str) and not valor.strip())
    if not es_vacio:
        texto = _validar_largo(validar_string_no_vacio(valor, nombre), nombre, maximo)

    return texto


def validar_precio(valor) -> Decimal:
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


def validar_servicio(body) -> dict:
    datos = validar_cuerpo_no_vacio(body)
    rechazar_campos_desconocidos(datos, CAMPOS_SERVICIO)

    return {
        'nombre': _validar_largo(validar_string_no_vacio(datos.get('nombre'), 'nombre'), 'nombre', NOMBRE_MAX),
        'descripcion': _texto_opcional(datos.get('descripcion'), 'descripcion', TEXTO_MAX),
        'precio': validar_precio(datos.get('precio')),
        'imagen_url': _texto_opcional(datos.get('imagen_url'), 'imagen_url', TEXTO_MAX),
        'activo': validar_booleano(datos.get('activo', True), 'activo'),
    }


def validar_estado(body) -> bool:
    datos = validar_cuerpo_no_vacio(body)
    rechazar_campos_desconocidos(datos, {'activo'})

    if 'activo' not in datos:
        raise ErrorAPI(
            code='required.activo',
            message="Campo requerido: 'activo'",
            description="El campo 'activo' es obligatorio"
        )

    return validar_booleano(datos['activo'], 'activo')


def leer_filtro_activo(args) -> bool | None:
    rechazar_campos_desconocidos(args, PARAMETROS_PAGINACION | {'activo'}, 'query string')
    activo = None
    if 'activo'in args:
        activo = validar_booleano(args['activo'], 'activo')
    return activo
