from datetime import date

import requests
from sqlalchemy.exc import IntegrityError

from ..constants import (
    BASE_URL,
    TMDB_API_BASE_URL,
    TMDB_API_KEY,
    TMDB_API_URL,
    TMDB_IMAGE_BASE_URL,
    TMDB_LANGUAGE,
    TMDB_TIMEOUT,
)
from ..paginacion import paginar
from ..repositories.peliculas import (
    actualizar_pelicula as guardar_actualizacion_pelicula,
    desactivar_pelicula as dar_baja_pelicula,
    importar_pelicula as guardar_pelicula,
    listar_peliculas as consultar_peliculas,
    obtener_pelicula_por_id,
    obtener_pelicula_por_tmdb_id,
)
from ..utils import ErrorAPI, formatear_fecha_hora
from ..validators.peliculas import (
    validar_id_pelicula,
    validar_parametros_busqueda_tmdb,
    validar_cuerpo_importacion_pelicula,
    validar_cuerpo_edicion_pelicula,
    validar_parametros_listado_peliculas,
)


def _formatear_pelicula(pelicula: dict) -> dict:
    pelicula['activa'] = bool(pelicula['activa'])
    pelicula['generos'] = [pelicula['genero']] if pelicula['genero'] else []
    pelicula['disponible_desde'] = formatear_fecha_hora(pelicula['disponible_desde'])
    pelicula['disponible_hasta'] = formatear_fecha_hora(pelicula['disponible_hasta'])
    return pelicula


def _error_pelicula_no_encontrada(id_pelicula: int) -> ErrorAPI:
    return ErrorAPI(
        code='pelicula.not.found',
        message='Pelicula no encontrada',
        description=f'No existe una pelicula con id {id_pelicula}',
        status=404,
    )


def _error_pelicula_ya_importada(tmdb_id: int) -> ErrorAPI:
    return ErrorAPI(
        code='pelicula.already.imported',
        message='Pelicula ya importada',
        description=f'La pelicula de TMDB con id {tmdb_id} ya existe en el catalogo',
        status=409,
    )


def _verificar_configuracion_tmdb() -> str:
    if not TMDB_API_KEY:
        raise ErrorAPI(
            code='tmdb.configuration.missing',
            message='Configuracion de TMDB incompleta',
            description="La variable de entorno 'TMDB_API_KEY' no esta configurada",
            status=503,
        )
    return TMDB_API_KEY


def listar_peliculas(args) -> dict:
    limit, offset, filtros = validar_parametros_listado_peliculas(args)
    peliculas, total = consultar_peliculas(limit, offset, filtros)
    peliculas = [_formatear_pelicula(pelicula) for pelicula in peliculas]

    return paginar(
        items=peliculas,
        total=total,
        limit=limit,
        offset=offset,
        recurso='peliculas',
        path=f'{BASE_URL}/peliculas',
        filtros=filtros,
    )


def buscar_pelicula(id_pelicula) -> dict:
    id_validado = validar_id_pelicula(id_pelicula)
    pelicula = obtener_pelicula_por_id(id_validado)

    if pelicula is None:
        raise _error_pelicula_no_encontrada(id_validado)

    return _formatear_pelicula(pelicula)


def actualizar_pelicula(id_pelicula, body) -> dict:
    id_validado = validar_id_pelicula(id_pelicula)
    datos = validar_cuerpo_edicion_pelicula(body)
    pelicula = guardar_actualizacion_pelicula(id_validado, datos)

    if pelicula is None:
        raise _error_pelicula_no_encontrada(id_validado)

    return _formatear_pelicula(pelicula)


def eliminar_pelicula(id_pelicula) -> dict:
    id_validado = validar_id_pelicula(id_pelicula)
    pelicula = dar_baja_pelicula(id_validado)

    if pelicula is None:
        raise _error_pelicula_no_encontrada(id_validado)

    return _formatear_pelicula(pelicula)


def _normalizar_detalle_tmdb(datos: dict, tmdb_id: int) -> dict:
    id_devuelto = datos.get('id')
    if (
        isinstance(id_devuelto, bool)
        or not isinstance(id_devuelto, int)
        or id_devuelto != tmdb_id
    ):
        raise _error_tmdb('El detalle devuelto no corresponde al ID solicitado')

    titulo = datos.get('title')
    sinopsis = datos.get('overview')
    poster_path = datos.get('poster_path')
    duracion_min = datos.get('runtime')
    generos = datos.get('genres')

    if not isinstance(titulo, str) or not titulo.strip():
        raise _error_tmdb('El detalle de TMDB no contiene un título válido')
    if sinopsis is None or sinopsis == '':
        sinopsis = ''
    elif not isinstance(sinopsis, str):
        raise _error_tmdb('El detalle de TMDB contiene una sinopsis inválida')
    if duracion_min is not None and (
        isinstance(duracion_min, bool) or not isinstance(duracion_min, int) or duracion_min < 0
    ):
        raise _error_tmdb('El detalle de TMDB contiene una duración inválida')
    poster_url = _construir_url_poster_tmdb(poster_path)
    if not isinstance(generos, list):
        raise _error_tmdb('El detalle de TMDB no contiene una lista de géneros válida')

    generos_normalizados = []
    for genero in generos:
        if not isinstance(genero, dict):
            raise _error_tmdb('El detalle de TMDB contiene un género inválido')
        id_genero = genero.get('id')
        nombre = genero.get('name')
        if (
            isinstance(id_genero, bool)
            or not isinstance(id_genero, int)
            or id_genero < 1
            or not isinstance(nombre, str)
            or not nombre.strip()
        ):
            raise _error_tmdb('El detalle de TMDB contiene un género inválido')
        generos_normalizados.append({'tmdb_id': id_genero, 'nombre': nombre.strip()})

    return {
        'tmdb_id': tmdb_id,
        'titulo': titulo.strip(),
        'sinopsis': sinopsis,
        'poster_url': poster_url,
        'duracion_min': duracion_min,
        'generos': generos_normalizados,
    }


def importar_pelicula(body) -> dict:
    tmdb_id = validar_cuerpo_importacion_pelicula(body)
    api_key = _verificar_configuracion_tmdb()

    if obtener_pelicula_por_tmdb_id(tmdb_id) is not None:
        raise _error_pelicula_ya_importada(tmdb_id)

    try:
        respuesta = requests.get(
            f'{TMDB_API_BASE_URL}/movie/{tmdb_id}',
            params={'api_key': api_key, 'language': TMDB_LANGUAGE},
            timeout=TMDB_TIMEOUT,
        )
    except requests.RequestException as error:
        raise _error_tmdb('TMDB no respondió correctamente', 'tmdb.unavailable') from error

    if respuesta.status_code == 404:
        raise ErrorAPI(
            code='tmdb.movie.not.found',
            message='Pelicula no encontrada en TMDB',
            description=f'TMDB no tiene una pelicula con id {tmdb_id}',
            status=404,
        )

    try:
        respuesta.raise_for_status()
        datos_tmdb = respuesta.json()
    except requests.exceptions.JSONDecodeError as error:
        raise _error_tmdb('TMDB no devolvió una respuesta JSON válida') from error
    except requests.RequestException as error:
        raise _error_tmdb('TMDB no respondió correctamente', 'tmdb.unavailable') from error

    if not isinstance(datos_tmdb, dict):
        raise _error_tmdb('TMDB devolvió un detalle con formato inválido')

    pelicula_tmdb = _normalizar_detalle_tmdb(datos_tmdb, tmdb_id)

    try:
        id_pelicula = guardar_pelicula(pelicula_tmdb)
    except IntegrityError as error:
        if obtener_pelicula_por_tmdb_id(tmdb_id) is None:
            raise
        raise _error_pelicula_ya_importada(tmdb_id) from error

    pelicula = obtener_pelicula_por_id(id_pelicula)
    if pelicula is None:
        raise RuntimeError(f'La pelicula importada con id {id_pelicula} no pudo recuperarse')

    return _formatear_pelicula(pelicula)


def _error_tmdb(descripcion: str, code: str = 'tmdb.invalid.response') -> ErrorAPI:
    return ErrorAPI(
        code=code,
        message='No se pudo completar la busqueda en TMDB',
        description=descripcion,
        status=502,
    )


def _construir_url_poster_tmdb(poster_path) -> str | None:
    if poster_path is None:
        return None
    if not isinstance(poster_path, str):
        raise _error_tmdb('TMDB devolvió una ruta de póster inválida')
    if poster_path == '':
        return None
    if not poster_path.startswith('/'):
        raise _error_tmdb('TMDB devolvió una ruta de póster inválida')
    return f'{TMDB_IMAGE_BASE_URL}{poster_path}'


def _normalizar_pelicula_tmdb(resultado: dict) -> dict:
    tmdb_id = resultado.get('id')
    titulo = resultado.get('title')
    titulo_original = resultado.get('original_title')
    sinopsis = resultado.get('overview')
    fecha_lanzamiento = resultado.get('release_date')
    poster_path = resultado.get('poster_path')
    tmdb_genero_ids = resultado.get('genre_ids')

    if isinstance(tmdb_id, bool) or not isinstance(tmdb_id, int) or tmdb_id < 1:
        raise _error_tmdb('Un resultado de TMDB no tiene un ID válido')
    if not isinstance(titulo, str) or not titulo.strip():
        raise _error_tmdb('Un resultado de TMDB no tiene un título válido')
    titulo = titulo.strip()
    if titulo_original is None or (isinstance(titulo_original, str) and not titulo_original.strip()):
        titulo_original = titulo
    elif not isinstance(titulo_original, str):
        raise _error_tmdb('Un resultado de TMDB contiene un título original inválido')
    else:
        titulo_original = titulo_original.strip()
    if sinopsis is None or sinopsis == '':
        sinopsis = ''
    elif not isinstance(sinopsis, str):
        raise _error_tmdb('Un resultado de TMDB contiene una sinopsis inválida')
    if not isinstance(tmdb_genero_ids, list) or any(
        isinstance(id_genero, bool) or not isinstance(id_genero, int) or id_genero < 1
        for id_genero in tmdb_genero_ids
    ):
        raise _error_tmdb('Un resultado de TMDB contiene IDs de género inválidos')
    if fecha_lanzamiento is None or fecha_lanzamiento == '':
        fecha_lanzamiento = None
    else:
        if not isinstance(fecha_lanzamiento, str):
            raise _error_tmdb('Un resultado de TMDB contiene una fecha inválida')
        try:
            fecha_parseada = date.fromisoformat(fecha_lanzamiento)
        except (TypeError, ValueError) as error:
            raise _error_tmdb('Un resultado de TMDB contiene una fecha inválida') from error
        if fecha_parseada.isoformat() != fecha_lanzamiento:
            raise _error_tmdb('Un resultado de TMDB contiene una fecha inválida')
    poster_url = _construir_url_poster_tmdb(poster_path)

    return {
        'tmdb_id': tmdb_id,
        'titulo': titulo,
        'titulo_original': titulo_original,
        'sinopsis': sinopsis,
        'fecha_lanzamiento': fecha_lanzamiento,
        'poster_url': poster_url,
        'tmdb_genero_ids': tmdb_genero_ids,
    }


def buscar_peliculas_tmdb(args) -> dict:
    query = validar_parametros_busqueda_tmdb(args)
    api_key = _verificar_configuracion_tmdb()

    try:
        respuesta = requests.get(
            TMDB_API_URL,
            params={
                'api_key': api_key,
                'query': query,
                'language': TMDB_LANGUAGE,
                'page': 1,
            },
            timeout=TMDB_TIMEOUT,
        )
        respuesta.raise_for_status()
        datos = respuesta.json()
    except requests.exceptions.JSONDecodeError as error:
        raise _error_tmdb('TMDB no devolvió una respuesta JSON válida') from error
    except requests.RequestException as error:
        raise _error_tmdb('TMDB no respondió correctamente', 'tmdb.unavailable') from error

    resultados = datos.get('results') if isinstance(datos, dict) else None
    if not isinstance(resultados, list) or any(
        not isinstance(resultado, dict) for resultado in resultados
    ):
        raise _error_tmdb("La respuesta de TMDB no contiene una lista válida de resultados")

    return {
        'resultados': [
            _normalizar_pelicula_tmdb(resultado)
            for resultado in resultados
        ],
    }
