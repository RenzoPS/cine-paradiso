from sqlalchemy import text

from . import ejecutar_consulta, ejecutar_escalar
from . import transaccion

CAMPOS_PELICULA = '''
    p.id_pelicula,
    p.tmdb_id,
    p.titulo,
    p.sinopsis,
    p.poster_url,
    p.duracion_min,
    p.clasificacion,
    p.genero,
    p.disponible_desde,
    p.disponible_hasta,
    CASE
        WHEN p.disponible_hasta IS NULL
          OR p.disponible_hasta >= UTC_TIMESTAMP() - INTERVAL 3 HOUR
        THEN TRUE
        ELSE FALSE
    END AS activa
'''


def _construir_filtros(filtros: dict) -> tuple[str, dict]:
    condiciones = []
    parametros = {}
    ahora_argentina = "UTC_TIMESTAMP() - INTERVAL 3 HOUR"

    if filtros.get('titulo') is not None:
        titulo = filtros['titulo'].replace('!', '!!').replace('%', '!%').replace('_', '!_')
        condiciones.append("LOWER(p.titulo) LIKE LOWER(:titulo) ESCAPE '!'")
        parametros['titulo'] = f'%{titulo}%'

    if filtros.get('genero') is not None:
        condiciones.append('LOWER(p.genero) = LOWER(:genero)')
        parametros['genero'] = filtros['genero']

    if filtros.get('clasificacion') is not None:
        condiciones.append('LOWER(p.clasificacion) = LOWER(:clasificacion)')
        parametros['clasificacion'] = filtros['clasificacion']

    if filtros.get('activa') is not None:
        if filtros['activa']:
            condiciones.append(
                '(p.disponible_hasta IS NULL OR '
                'p.disponible_hasta >= UTC_TIMESTAMP() - INTERVAL 3 HOUR)'
            )
        else:
            condiciones.append(
                'p.disponible_hasta < UTC_TIMESTAMP() - INTERVAL 3 HOUR'
            )

    if filtros.get('fecha') is not None:
        condiciones.append(f":fecha >= DATE({ahora_argentina})")
        parametros['fecha'] = filtros['fecha']

    def existe_funcion_futura() -> str:
        condiciones_funcion = [
            'f.fk_id_pelicula = p.id_pelicula',
            f'f.fecha_hora > {ahora_argentina}',
        ]
        join_salas = ''

        if filtros.get('id_local') is not None:
            join_salas = 'JOIN salas s ON s.id_sala = f.fk_id_sala'
            condiciones_funcion.append('s.fk_id_local = :id_local')
            parametros['id_local'] = filtros['id_local']

        if filtros.get('fecha') is not None:
            condiciones_funcion.extend((
                'f.fecha_hora >= :fecha',
                'f.fecha_hora < DATE_ADD(:fecha, INTERVAL 1 DAY)',
            ))

        return f'''
            EXISTS (
                SELECT 1
                FROM funciones f
                {join_salas}
                WHERE {' AND '.join(condiciones_funcion)}
            )
        '''

    if filtros.get('en_cartel') is not None:
        condicion_cartel = f'''
            (
                p.disponible_hasta >= {ahora_argentina}
                AND p.disponible_desde IS NOT NULL
                AND p.disponible_hasta IS NOT NULL
                AND p.disponible_desde <= {ahora_argentina}
                AND {existe_funcion_futura()}
            )
        '''
        if filtros['en_cartel']:
            condiciones.append(condicion_cartel)
        else:
            condiciones.append(f'NOT {condicion_cartel}')
    elif filtros.get('id_local') is not None or filtros.get('fecha') is not None:
        condiciones.append(existe_funcion_futura())

    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ''
    return where, parametros


def listar_peliculas(limit: int, offset: int, filtros: dict) -> tuple[list[dict], int]:
    where, parametros_filtro = _construir_filtros(filtros)
    total = ejecutar_escalar(
        f'SELECT COUNT(*) FROM peliculas p {where}',
        parametros_filtro,
    ) or 0

    peliculas = ejecutar_consulta(
        f'''
        SELECT {CAMPOS_PELICULA}
        FROM peliculas p
        {where}
        ORDER BY p.id_pelicula
        LIMIT :limit OFFSET :offset
        ''',
        {**parametros_filtro, 'limit': limit, 'offset': offset},
    )

    return peliculas, total


def obtener_pelicula_por_id(id_pelicula: int) -> dict | None:
    peliculas = ejecutar_consulta(
        f'''
        SELECT {CAMPOS_PELICULA}
        FROM peliculas p
        WHERE p.id_pelicula = :id_pelicula
        ''',
        {'id_pelicula': id_pelicula},
    )

    if not peliculas:
        return None

    return peliculas[0]


def obtener_pelicula_por_tmdb_id(tmdb_id: int) -> dict | None:
    peliculas = ejecutar_consulta(
        f'''
        SELECT {CAMPOS_PELICULA}
        FROM peliculas p
        WHERE p.tmdb_id = :tmdb_id
        ''',
        {'tmdb_id': tmdb_id},
    )
    return peliculas[0] if peliculas else None


def actualizar_pelicula(id_pelicula: int, datos: dict) -> dict | None:
    with transaccion() as conexion:
        existe = conexion.execute(
            text(
                '''
                SELECT id_pelicula
                FROM peliculas
                WHERE id_pelicula = :id_pelicula
                FOR UPDATE
                '''
            ),
            {'id_pelicula': id_pelicula},
        ).scalar_one_or_none()

        if existe is None:
            return None

        conexion.execute(
            text(
                '''
                UPDATE peliculas
                SET sinopsis = :sinopsis,
                    poster_url = :poster_url,
                    clasificacion = :clasificacion,
                    disponible_desde = :disponible_desde,
                    disponible_hasta = :disponible_hasta
                WHERE id_pelicula = :id_pelicula
                '''
            ),
            {**datos, 'id_pelicula': id_pelicula},
        )

    return obtener_pelicula_por_id(id_pelicula)


def desactivar_pelicula(id_pelicula: int) -> dict | None:
    with transaccion() as conexion:
        existe = conexion.execute(
            text(
                '''
                SELECT id_pelicula
                FROM peliculas
                WHERE id_pelicula = :id_pelicula
                FOR UPDATE
                '''
            ),
            {'id_pelicula': id_pelicula},
        ).scalar_one_or_none()

        if existe is None:
            return None

        conexion.execute(
            text(
                '''
                UPDATE peliculas
                SET disponible_desde = CASE
                        WHEN disponible_desde IS NULL
                          OR disponible_desde > UTC_TIMESTAMP() - INTERVAL 3 HOUR - INTERVAL 2 SECOND
                        THEN UTC_TIMESTAMP() - INTERVAL 3 HOUR - INTERVAL 2 SECOND
                        ELSE disponible_desde
                    END,
                    disponible_hasta = UTC_TIMESTAMP() - INTERVAL 3 HOUR - INTERVAL 1 SECOND
                WHERE id_pelicula = :id_pelicula
                '''
            ),
            {'id_pelicula': id_pelicula},
        )

    return obtener_pelicula_por_id(id_pelicula)


def importar_pelicula(datos: dict) -> int:
    with transaccion() as conexion:
        resultado = conexion.execute(
            text(
                '''
                INSERT INTO peliculas
                    (tmdb_id, titulo, sinopsis, poster_url, duracion_min, clasificacion, genero,
                     disponible_desde, disponible_hasta)
                VALUES
                    (:tmdb_id, :titulo, :sinopsis, :poster_url, :duracion_min, NULL, :genero,
                     NULL, NULL)
                '''
            ),
            {
                'tmdb_id': datos['tmdb_id'],
                'titulo': datos['titulo'],
                'sinopsis': datos['sinopsis'],
                'poster_url': datos['poster_url'],
                'duracion_min': datos['duracion_min'],
                'genero': datos['generos'][0]['nombre'] if datos['generos'] else None,
            },
        )
        id_pelicula = resultado.lastrowid

    return id_pelicula
