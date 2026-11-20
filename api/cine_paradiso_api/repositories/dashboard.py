from ..constants import ESTADO_CANCELADA, ESTADO_PAGADA, ESTADO_USADA
from . import ejecutar_consulta


def listar_funciones_con_ventas() -> list[dict]:
    return ejecutar_consulta(
        """
        SELECT
            f.id_funcion,
            f.fecha_hora,
            p.id_pelicula,
            p.titulo AS pelicula,
            p.genero,
            s.nombre AS sala,
            l.nombre AS local,
            (
                SELECT COUNT(*)
                FROM butacas b
                WHERE b.fk_id_sala = f.fk_id_sala
            ) AS capacidad,
            (
                SELECT COUNT(*)
                FROM entradas e
                JOIN compras c ON c.id_compra = e.fk_id_compra
                WHERE e.fk_id_funcion = f.id_funcion
                  AND c.estado IN (:estado_pagada, :estado_usada)
            ) AS vendidas
        FROM funciones f
        JOIN peliculas p ON p.id_pelicula = f.fk_id_pelicula
        JOIN salas s ON s.id_sala = f.fk_id_sala
        JOIN locales l ON l.id_local = s.fk_id_local
        ORDER BY f.fecha_hora, f.id_funcion
        """,
        {'estado_pagada': ESTADO_PAGADA, 'estado_usada': ESTADO_USADA},
    )


def listar_cancelaciones_por_pelicula() -> list[dict]:
    return ejecutar_consulta(
        """
        SELECT
            p.id_pelicula,
            p.titulo AS pelicula,
            COUNT(*) AS cancelaciones
        FROM compras c
        JOIN funciones f ON f.id_funcion = c.fk_id_funcion
        JOIN peliculas p ON p.id_pelicula = f.fk_id_pelicula
        WHERE c.estado = :estado_cancelada
        GROUP BY p.id_pelicula, p.titulo
        ORDER BY cancelaciones DESC, p.titulo
        """,
        {'estado_cancelada': ESTADO_CANCELADA},
    )
