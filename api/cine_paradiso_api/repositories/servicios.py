from sqlalchemy import text

from . import ejecutar_consulta, ejecutar_mutacion, listar_paginado

CAMPOS_SERVICIO = 'id_servicio, nombre, descripcion, precio, activo'


def listar_servicios(activo: bool, limit: int, offset: int) -> tuple[list[dict], int]:
    return listar_paginado('servicios', {'activo = ?': activo}, 'nombre', limit, offset)


def obtener_servicio_por_id(id_servicio: int) -> dict | None:
    filas = ejecutar_consulta(
        f'SELECT {CAMPOS_SERVICIO} FROM servicios WHERE id_servicio = :id_servicio',
        {'id_servicio': id_servicio},
    )

    return filas[0] if filas else None


def insertar_servicio(datos: dict) -> int:
    return ejecutar_mutacion(
        """
        INSERT INTO servicios (nombre, descripcion, precio, activo)
        VALUES (:nombre, :descripcion, :precio, :activo)
        """,
        datos,
    )


def actualizar_servicio(id_servicio: int, datos: dict) -> None:
    ejecutar_mutacion(
        """
        UPDATE servicios
        SET nombre = :nombre, descripcion = :descripcion, precio = :precio, activo = :activo
        WHERE id_servicio = :id_servicio
        """,
        {**datos, 'id_servicio': id_servicio},
    )


def desactivar_servicio(id_servicio: int) -> None:
    ejecutar_mutacion(
        'UPDATE servicios SET activo = FALSE WHERE id_servicio = :id_servicio',
        {'id_servicio': id_servicio},
    )


def reemplazar_servicios_de_compra(conexion, id_compra: int, items: list[dict]) -> int | None:
    """
    Deja en la compra exactamente los servicios de `items`.
    Devuelve el id del primer servicio inexistente o dado de baja, o None si todos se guardaron.
    """
    conexion.execute(
        text('DELETE FROM compras_servicios WHERE fk_id_compra = :id_compra'),
        {'id_compra': id_compra},
    )

    servicio_no_disponible = None

    for item in items:
        resultado = conexion.execute(
            text("""
                INSERT INTO compras_servicios (fk_id_compra, fk_id_servicio, cantidad)
                SELECT :id_compra, id_servicio, :cantidad
                FROM servicios
                WHERE id_servicio = :id_servicio AND activo = TRUE
            """),
            {
                'id_compra': id_compra,
                'id_servicio': item['id_servicio'],
                'cantidad': item['cantidad'],
            },
        )

        if resultado.rowcount == 0:
            servicio_no_disponible = item['id_servicio']
            break

    return servicio_no_disponible
