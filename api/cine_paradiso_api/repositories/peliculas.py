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
    p.disponible_desde,
    p.disponible_hasta,
    p.activa
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
        condiciones.append(
            '''
            EXISTS (
                SELECT 1
                FROM peliculas_generos pg_filtro
                JOIN generos g_filtro ON g_filtro.id_genero = pg_filtro.fk_id_genero
                WHERE pg_filtro.fk_id_pelicula = p.id_pelicula
                  AND LOWER(g_filtro.nombre) = LOWER(:genero)
            )
            '''
        )
        parametros['genero'] = filtros['genero']

    if filtros.get('clasificacion') is not None:
        condiciones.append('LOWER(p.clasificacion) = LOWER(:clasificacion)')
        parametros['clasificacion'] = filtros['clasificacion']

    if filtros.get('activa') is not None:
        condiciones.append('p.activa = :activa')
        parametros['activa'] = filtros['activa']

    if filtros.get('fecha') is not None:
        condiciones.append(f":fecha >= DATE({ahora_argentina})")
        parametros['fecha'] = filtros['fecha']

    def existe_funcion_futura() -> str:
        condiciones_funcion = [
            'f.fk_id_pelicula = p.id_pelicula',
            'f.activa = TRUE',
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
                p.activa = TRUE
                AND p.disponible_desde IS NOT NULL
                AND p.disponible_hasta IS NOT NULL
                AND p.disponible_desde <= {ahora_argentina}
                AND p.disponible_hasta >= {ahora_argentina}
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


def obtener_generos_por_peliculas(ids_peliculas: list[int]) -> dict[int, list[str]]:
    if not ids_peliculas:
        return {}

    parametros = {f'id_{indice}': id_pelicula for indice, id_pelicula in enumerate(ids_peliculas)}
    placeholders = ', '.join(f':{nombre}' for nombre in parametros)
    filas = ejecutar_consulta(
        f'''
        SELECT pg.fk_id_pelicula AS id_pelicula, g.nombre AS genero
        FROM peliculas_generos pg
        JOIN generos g ON g.id_genero = pg.fk_id_genero
        WHERE pg.fk_id_pelicula IN ({placeholders})
        ORDER BY pg.fk_id_pelicula, g.nombre
        ''',
        parametros,
    )

    generos = {id_pelicula: [] for id_pelicula in ids_peliculas}
    for fila in filas:
        generos[fila['id_pelicula']].append(fila['genero'])
    return generos


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

    generos = obtener_generos_por_peliculas([pelicula['id_pelicula'] for pelicula in peliculas])
    for pelicula in peliculas:
        pelicula['generos'] = generos[pelicula['id_pelicula']]

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

    pelicula = peliculas[0]
    generos = obtener_generos_por_peliculas([id_pelicula])
    pelicula['generos'] = generos[id_pelicula]
    return pelicula


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
                SET activa = FALSE
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
                    (tmdb_id, titulo, sinopsis, poster_url, duracion_min, clasificacion,
                     disponible_desde, disponible_hasta, activa)
                VALUES
                    (:tmdb_id, :titulo, :sinopsis, :poster_url, :duracion_min, NULL,
                     NULL, NULL, TRUE)
                '''
            ),
            {
                'tmdb_id': datos['tmdb_id'],
                'titulo': datos['titulo'],
                'sinopsis': datos['sinopsis'],
                'poster_url': datos['poster_url'],
                'duracion_min': datos['duracion_min'],
            },
        )
        id_pelicula = resultado.lastrowid

        for genero in datos['generos']:
            conexion.execute(
                text(
                    '''
                    INSERT INTO generos (tmdb_id, nombre)
                    VALUES (:tmdb_id, :nombre)
                    ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)
                    '''
                ),
                {'tmdb_id': genero['tmdb_id'], 'nombre': genero['nombre']},
            )
            id_genero = conexion.execute(
                text('SELECT id_genero FROM generos WHERE tmdb_id = :tmdb_id'),
                {'tmdb_id': genero['tmdb_id']},
            ).scalar_one()
            conexion.execute(
                text(
                    '''
                    INSERT IGNORE INTO peliculas_generos (fk_id_pelicula, fk_id_genero)
                    VALUES (:id_pelicula, :id_genero)
                    '''
                ),
                {'id_pelicula': id_pelicula, 'id_genero': id_genero},
            )

    return id_pelicula
