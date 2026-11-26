from decimal import Decimal, InvalidOperation

from ..paginacion import PARAMETROS_PAGINACION, leer_parametros_paginacion
from ..utils import (
    ErrorAPI,
    parsear_fecha,
    parsear_fecha_hora,
    rechazar_campos_desconocidos,
    validar_cuerpo_no_vacio,
    validar_entero_positivo,
    validar_string_no_vacio,
)


PARAMETROS_FILTRO_LISTADO = {'id_pelicula', 'id_local', 'fecha', 'incluir_canceladas'}
CAMPOS_FUNCION = {'id_pelicula', 'id_sala', 'fecha_hora', 'precio'}
PRECIO_MAXIMO = Decimal('99999999.99')


def validar_id_funcion(id_funcion) -> int:
    return validar_entero_positivo(id_funcion, 'id_funcion')


def validar_parametros_listado_funciones(args) -> tuple[int, int, dict]:
    rechazar_campos_desconocidos(
        args,
        PARAMETROS_PAGINACION | PARAMETROS_FILTRO_LISTADO,
        'parametros de consulta',
    )
    limit, offset = leer_parametros_paginacion(args)
    filtros = {}

    for campo in ('id_pelicula', 'id_local'):
        if args.get(campo) is not None:
            filtros[campo] = validar_entero_positivo(args.get(campo), campo)

    if args.get('fecha') is not None:
        fecha_texto = validar_string_no_vacio(args.get('fecha'), 'fecha')
        fecha = parsear_fecha(fecha_texto, 'fecha')
        if fecha.strftime('%Y-%m-%d') != fecha_texto:
            raise ErrorAPI(
                code='invalid.format',
                message="Formato de 'fecha' invalido",
                description="El parametro 'fecha' debe usar el formato YYYY-MM-DD"
            )
        filtros['fecha'] = fecha.date()

    if args.get('incluir_canceladas') is not None:
        # Convertir a boolean: 'true', '1', 'yes' -> True; cualquier otro -> False
        valor = str(args.get('incluir_canceladas')).lower()
        filtros['incluir_canceladas'] = valor in ('true', '1', 'yes', 'on')

    return limit, offset, filtros


def validar_cuerpo_funcion(body) -> dict:
    datos = validar_cuerpo_no_vacio(body, 'cuerpo')
    rechazar_campos_desconocidos(datos, CAMPOS_FUNCION)

    for campo in sorted(CAMPOS_FUNCION):
        if campo not in datos:
            raise ErrorAPI(
                code=f'required.{campo}',
                message=f"Campo requerido: '{campo}'",
                description=f"El campo '{campo}' es obligatorio"
            )

    precio_original = datos['precio']
    if isinstance(precio_original, bool):
        raise _error_precio()

    try:
        precio = Decimal(str(precio_original))
    except (InvalidOperation, ValueError):
        raise _error_precio()

    if not precio.is_finite():
        raise _error_precio()
    if precio < 0:
        raise ErrorAPI(
            code='invalid.min.value',
            message="Valor por debajo del minimo permitido para 'precio'",
            description="El campo 'precio' debe ser mayor o igual a 0"
        )
    if precio > PRECIO_MAXIMO:
        raise ErrorAPI(
            code='invalid.max.value',
            message="Valor por encima del maximo permitido para 'precio'",
            description="El campo 'precio' no puede superar 99999999.99"
        )
    try:
        tiene_hasta_dos_decimales = precio.quantize(Decimal('0.01')) == precio
    except InvalidOperation:
        tiene_hasta_dos_decimales = False
    if not tiene_hasta_dos_decimales:
        raise _error_precio()

    return {
        'id_pelicula': validar_entero_positivo(datos['id_pelicula'], 'id_pelicula'),
        'id_sala': validar_entero_positivo(datos['id_sala'], 'id_sala'),
        'fecha_hora': parsear_fecha_hora(datos['fecha_hora'], 'fecha_hora'),
        'precio': precio,
    }


def _error_precio() -> ErrorAPI:
    return ErrorAPI(
        code='invalid.format',
        message="Formato de 'precio' invalido",
        description="El campo 'precio' debe ser un numero decimal con hasta dos posiciones"
    )
