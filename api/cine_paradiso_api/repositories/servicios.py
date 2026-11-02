from . import ejecutar_consulta, ejecutar_mutacion, listar_paginado

COLUMNAS_SERVICIO = 'id, nombre, descripcion, precio, imagen_url, activo'


def listar(activo: bool | None, limit: int, offset: int) -> tuple[list[dict], int]:
    return listar_paginado('servicio', {'activo = ?': activo}, 'nombre', limit, offset)


def obtener_por_id(servicio_id: int) -> dict | None:
    filas = ejecutar_consulta(
        f'SELECT {COLUMNAS_SERVICIO} FROM servicio WHERE id = :id',
        {'id': servicio_id},
    )

    return filas[0] if filas else None


def crear(datos: dict) -> int:
    return ejecutar_mutacion(
        'INSERT INTO servicio (nombre, descripcion, precio, imagen_url, activo) '
        'VALUES (:nombre, :descripcion, :precio, :imagen_url, :activo)',
        datos,
    )


def actualizar(servicio_id: int, datos: dict) -> None:
    ejecutar_mutacion(
        'UPDATE servicio SET nombre = :nombre, descripcion = :descripcion, precio = :precio, '
        'imagen_url = :imagen_url, activo = :activo WHERE id = :id',
        {**datos, 'id': servicio_id},
    )


def cambiar_estado(servicio_id: int, activo: bool) -> None:
    ejecutar_mutacion(
        'UPDATE servicio SET activo = :activo WHERE id = :id',
        {'activo': activo, 'id': servicio_id},
    )
