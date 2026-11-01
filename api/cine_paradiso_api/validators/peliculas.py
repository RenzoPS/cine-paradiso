from datetime import datetime
from urllib.parse import urlsplit

from ..paginacion import PARAMETROS_PAGINACION, leer_parametros_paginacion
from ..utils import (
    ErrorAPI,
    parsear_fecha_hora,
    rechazar_campos_desconocidos,
    validar_booleano,
    validar_cuerpo_no_vacio,
    validar_entero_positivo,
    validar_string_no_vacio,
)

PARAMETROS_FILTRO_LISTADO = {'titulo', 'genero', 'clasificacion', 'activa'}
CAMPOS_EDITABLES_PELICULA = {
    'sinopsis',
    'poster_url',
    'clasificacion',
    'disponible_desde',
    'disponible_hasta',
}


def validar_id_pelicula(id_pelicula) -> int:
    return validar_entero_positivo(id_pelicula, 'id_pelicula')


def validar_parametros_listado_peliculas(args) -> tuple[int, int, dict]:
    rechazar_campos_desconocidos(
        args,
        PARAMETROS_PAGINACION | PARAMETROS_FILTRO_LISTADO,
        'parametros de consulta',
    )
    limit, offset = leer_parametros_paginacion(args)
    filtros = {}

    for campo in ('titulo', 'genero', 'clasificacion'):
        valor = args.get(campo)
        if valor is not None:
            filtros[campo] = validar_string_no_vacio(valor, campo)

    if args.get('activa') is not None:
        filtros['activa'] = validar_booleano(args.get('activa'), 'activa')

    return limit, offset, filtros


def validar_parametros_busqueda_tmdb(args) -> str:
    rechazar_campos_desconocidos(args, {'q'}, 'parametros de consulta')
    return validar_string_no_vacio(args.get('q'), 'q')


def validar_cuerpo_importacion_pelicula(body) -> int:
    datos = validar_cuerpo_no_vacio(body, 'cuerpo')
    rechazar_campos_desconocidos(datos, {'tmdb_id'})
    return validar_entero_positivo(datos.get('tmdb_id'), 'tmdb_id')


def validar_cuerpo_edicion_pelicula(body) -> dict[str, str | datetime | None]:
    datos = validar_cuerpo_no_vacio(body, 'cuerpo')
    rechazar_campos_desconocidos(datos, CAMPOS_EDITABLES_PELICULA)

    for campo in sorted(CAMPOS_EDITABLES_PELICULA):
        if campo not in datos:
            raise ErrorAPI(
                code=f'required.{campo}',
                message=f"Campo requerido: '{campo}'",
                description=f"El campo '{campo}' es obligatorio en la edición completa"
            )

    sinopsis = _validar_texto_nullable(datos['sinopsis'], 'sinopsis')
    poster_url = _validar_texto_nullable(datos['poster_url'], 'poster_url')
    if poster_url is not None:
        try:
            url = urlsplit(poster_url)
            puerto = url.port
            url_valida = (
                url.scheme in ('http', 'https')
                and bool(url.hostname)
                and (puerto is None or 1 <= puerto <= 65535)
            )
        except ValueError:
            url_valida = False

        if not url_valida:
            raise ErrorAPI(
                code='invalid.format',
                message="Formato de 'poster_url' invalido",
                description="El campo 'poster_url' debe ser una URL HTTP o HTTPS valida"
            )

    clasificacion = _validar_texto_nullable(datos['clasificacion'], 'clasificacion')
    disponible_desde = _validar_fecha_hora_nullable(datos['disponible_desde'], 'disponible_desde')
    disponible_hasta = _validar_fecha_hora_nullable(datos['disponible_hasta'], 'disponible_hasta')

    if (disponible_desde is None) != (disponible_hasta is None):
        raise ErrorAPI(
            code='invalid.format',
            message='Periodo de disponibilidad incompleto',
            description="Los campos 'disponible_desde' y 'disponible_hasta' deben ser ambos nulos o ambos estar informados"
        )

    if (
        disponible_desde is not None
        and disponible_hasta is not None
        and disponible_desde > disponible_hasta
    ):
        raise ErrorAPI(
            code='invalid.format',
            message='Periodo de disponibilidad invalido',
            description="'disponible_desde' no puede ser posterior a 'disponible_hasta'"
        )

    return {
        'sinopsis': sinopsis,
        'poster_url': poster_url,
        'clasificacion': clasificacion,
        'disponible_desde': disponible_desde,
        'disponible_hasta': disponible_hasta,
    }


def _validar_texto_nullable(valor, nombre: str) -> str | None:
    if valor is None:
        return None
    return validar_string_no_vacio(valor, nombre)


def _validar_fecha_hora_nullable(valor, nombre: str) -> datetime | None:
    if valor is None:
        return None
    return parsear_fecha_hora(valor, nombre)
