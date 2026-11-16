from sqlalchemy import text

from . import ejecutar_consulta, ejecutar_escalar

CAMPOS_FUNCION = '''
    f.id_funcion,
    p.id_pelicula,
    p.titulo AS pelicula,
    p.poster_url,
    p.duracion_min,
    s.id_sala,
    s.nombre AS sala,
    l.id_local,
    l.nombre AS local,
    l.direccion,
    f.fecha_hora,
    f.precio
'''

TABLAS_FUNCION = '''
    FROM funciones f
    JOIN peliculas p ON p.id_pelicula = f.fk_id_pelicula
    JOIN salas s ON s.id_sala = f.fk_id_sala
    JOIN locales l ON l.id_local = s.fk_id_local
'''


def _construir_filtros(filtros: dict) -> tuple[str, dict]:
    condiciones = ['f.fecha_hora > UTC_TIMESTAMP() - INTERVAL 3 HOUR']
    parametros = {}

    if filtros.get('id_pelicula') is not None:
        condiciones.append('f.fk_id_pelicula = :id_pelicula')
        parametros['id_pelicula'] = filtros['id_pelicula']

    if filtros.get('id_local') is not None:
        condiciones.append('s.fk_id_local = :id_local')
        parametros['id_local'] = filtros['id_local']

    condiciones.append(
        'f.fecha_hora BETWEEN p.disponible_desde AND p.disponible_hasta'
    )

    if filtros.get('fecha') is not None:
        condiciones.extend((
            'f.fecha_hora >= :fecha',
            'f.fecha_hora < DATE_ADD(:fecha, INTERVAL 1 DAY)',
        ))
        parametros['fecha'] = filtros['fecha']

    return f"WHERE {' AND '.join(condiciones)}", parametros


def listar_funciones(limit: int, offset: int, filtros: dict) -> tuple[list[dict], int]:
    where, parametros_filtro = _construir_filtros(filtros)
    total = ejecutar_escalar(
        f'SELECT COUNT(*) {TABLAS_FUNCION} {where}',
        parametros_filtro,
    ) or 0

    funciones = ejecutar_consulta(
        f'''
        SELECT {CAMPOS_FUNCION}
        {TABLAS_FUNCION}
        {where}
        ORDER BY f.fecha_hora, f.id_funcion
        LIMIT :limit OFFSET :offset
        ''',
        {**parametros_filtro, 'limit': limit, 'offset': offset},
    )

    return funciones, total


def obtener_funcion_por_id(id_funcion: int) -> dict | None:
    funciones = ejecutar_consulta(
        f'''
        SELECT {CAMPOS_FUNCION}
        {TABLAS_FUNCION}
        WHERE f.id_funcion = :id_funcion
        ''',
        {'id_funcion': id_funcion},
    )

    return funciones[0] if funciones else None


def listar_salas() -> list[dict]:
    return ejecutar_consulta(
        '''
        SELECT s.id_sala, s.nombre AS sala, l.id_local, l.nombre AS local, l.direccion
        FROM salas s
        JOIN locales l ON l.id_local = s.fk_id_local
        ORDER BY l.id_local, s.id_sala
        '''
    )


def bloquear_sala(conexion, id_sala: int) -> int | None:
    return conexion.execute(
        text('SELECT id_sala FROM salas WHERE id_sala = :id_sala FOR UPDATE'),
        {'id_sala': id_sala},
    ).scalar_one_or_none()


def obtener_pelicula_para_funcion(conexion, id_pelicula: int) -> dict | None:
    pelicula = conexion.execute(
        text(
            '''
            SELECT duracion_min, disponible_desde, disponible_hasta
            FROM peliculas
            WHERE id_pelicula = :id_pelicula
            FOR UPDATE
            '''
        ),
        {'id_pelicula': id_pelicula},
    ).mappings().one_or_none()

    return dict(pelicula) if pelicula is not None else None


def obtener_hora_actual(conexion):
    return conexion.execute(
        text('SELECT UTC_TIMESTAMP() - INTERVAL 3 HOUR')
    ).scalar_one()


def obtener_funcion_superpuesta(
    conexion,
    id_sala: int,
    inicio,
    fin,
    id_funcion: int | None = None,
) -> int | None:
    excluir_funcion = ''
    parametros = {'id_sala': id_sala, 'inicio': inicio, 'fin': fin}
    if id_funcion is not None:
        excluir_funcion = 'AND f.id_funcion != :id_funcion'
        parametros['id_funcion'] = id_funcion

    return conexion.execute(
        text(
            f'''
            SELECT f.id_funcion
            FROM funciones f
            JOIN peliculas p ON p.id_pelicula = f.fk_id_pelicula
            WHERE f.fk_id_sala = :id_sala
              {excluir_funcion}
              AND f.fecha_hora < :fin
              AND CASE
                    WHEN p.duracion_min IS NULL OR p.duracion_min < 1
                    THEN '9999-12-31 23:59:59'
                    ELSE DATE_ADD(f.fecha_hora, INTERVAL p.duracion_min MINUTE)
                  END > :inicio
            LIMIT 1
            '''
        ),
        parametros,
    ).scalar_one_or_none()


def obtener_sala_de_funcion(conexion, id_funcion: int) -> int | None:
    return conexion.execute(
        text(
            '''
            SELECT fk_id_sala
            FROM funciones
            WHERE id_funcion = :id_funcion
            FOR UPDATE
            '''
        ),
        {'id_funcion': id_funcion},
    ).scalar_one_or_none()


def obtener_compra_de_funcion(conexion, id_funcion: int) -> int | None:
    return conexion.execute(
        text(
            '''
            SELECT id_compra
            FROM compras
            WHERE fk_id_funcion = :id_funcion
              AND estado IN ('pendiente', 'pagada')
            LIMIT 1
            FOR UPDATE
            '''
        ),
        {'id_funcion': id_funcion},
    ).scalar_one_or_none()


def insertar_funcion(conexion, datos: dict) -> int:
    resultado = conexion.execute(
        text(
            '''
            INSERT INTO funciones (fk_id_pelicula, fk_id_sala, fecha_hora, precio)
            VALUES (:id_pelicula, :id_sala, :fecha_hora, :precio)
            '''
        ),
        datos,
    )
    return resultado.lastrowid


def actualizar_funcion_sql(conexion, id_funcion: int, datos: dict) -> None:
    conexion.execute(
        text(
            '''
            UPDATE funciones
            SET fk_id_pelicula = :id_pelicula,
                fk_id_sala = :id_sala,
                fecha_hora = :fecha_hora,
                precio = :precio
            WHERE id_funcion = :id_funcion
            '''
        ),
        {**datos, 'id_funcion': id_funcion},
    )
