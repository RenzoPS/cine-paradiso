from datetime import datetime

from sqlalchemy import bindparam, text

from ..constants import ESTADO_PAGADA, ESTADO_PENDIENTE, ESTADO_USADA, ESTADO_VENCIDA
from . import ejecutar_consulta, fila_a_dict, transaccion

def obtener_compra_por_id(id_compra: int) -> dict | None:
    filas = ejecutar_consulta(
        """
        SELECT id_compra, fk_id_usuario, fk_id_funcion, estado, fecha_hora
        FROM compras
        WHERE id_compra = :id_compra
        """,
        {'id_compra': id_compra},
    )
    return filas[0] if filas else None


def obtener_entradas_de_compra(id_compra: int) -> list[dict]:
    sql = """
        SELECT b.id_butaca, b.fila, b.numero
        FROM entradas e
        JOIN butacas b ON b.id_butaca = e.fk_id_butaca
        WHERE e.fk_id_compra = :id_compra
        ORDER BY b.fila, b.numero
    """
    return ejecutar_consulta(sql, {'id_compra': id_compra})


def obtener_servicios_de_compra(id_compra: int) -> list[dict]:
    sql = """
        SELECT s.id_servicio, s.nombre, s.precio, cs.cantidad
        FROM compras_servicios cs
        JOIN servicios s ON s.id_servicio = cs.fk_id_servicio
        WHERE cs.fk_id_compra = :id_compra
        ORDER BY s.nombre
    """
    return ejecutar_consulta(sql, {'id_compra': id_compra})


def obtener_datos_para_mail(id_compra: int) -> dict:
    """
    Email del cliente y datos de la funcion para armar el mail. Devuelve {} si no existe.
    """
    sql = """
        SELECT u.email, p.titulo, sa.nombre AS sala, f.fecha_hora
        FROM compras c
        JOIN usuarios u ON u.id_usuario = c.fk_id_usuario
        JOIN funciones f ON f.id_funcion = c.fk_id_funcion
        JOIN peliculas p ON p.id_pelicula = f.fk_id_pelicula
        JOIN salas sa ON sa.id_sala = f.fk_id_sala
        WHERE c.id_compra = :id_compra
    """
    filas = ejecutar_consulta(sql, {'id_compra': id_compra})
    return filas[0] if filas else {}


def actualizar_compra_pagada(id_compra: int) -> bool:
    """
    Pasa la compra de pendiente a pagada. Devuelve False si ya no estaba pendiente.
    """
    sql = """
        UPDATE compras
        SET estado = :estado_pagada
        WHERE id_compra = :id_compra
          AND estado = :estado_pendiente
    """
    with transaccion() as conexion:
        resultado = conexion.execute(text(sql), {
            'id_compra': id_compra,
            'estado_pagada': ESTADO_PAGADA,
            'estado_pendiente': ESTADO_PENDIENTE,
        })
        return resultado.rowcount > 0


def obtener_fecha_hora_funcion(id_funcion: int) -> datetime | None:
    """
    Fecha y hora de la funcion, para validar que el QR se use el dia correcto.
    """
    sql = """
        SELECT fecha_hora
        FROM funciones
        WHERE id_funcion = :id_funcion
    """
    filas = ejecutar_consulta(sql, {'id_funcion': id_funcion})
    return filas[0]['fecha_hora'] if filas else None


def guardar_qr_token(id_compra: int, qr_token: str) -> None:
    """
    Guarda el token del QR la primera vez que se genera.
    """
    sql = """
        UPDATE compras
        SET qr_token = :qr_token
        WHERE id_compra = :id_compra
            AND qr_token IS NULL
    """
    with transaccion() as conexion:
        conexion.execute(text(sql), {'id_compra': id_compra, 'qr_token': qr_token})


def marcar_compra_usada(id_compra: int, fecha_validacion: datetime) -> bool:
    """
    Pasa la compra de pagada a usada. Devuelve False si ya no estaba pagada: asi dos escaneos simultaneos no validan la misma compra.
    """
    sql = """
        UPDATE compras
        SET estado = :estado_usada,
            fecha_validacion = :fecha_validacion
        WHERE id_compra = :id_compra
            AND estado = :estado_pagada
    """
    with transaccion() as conexion:
        resultado = conexion.execute(text(sql), {
            'id_compra': id_compra,
            'fecha_validacion': fecha_validacion,
            'estado_usada': ESTADO_USADA,
            'estado_pagada': ESTADO_PAGADA,
        })
        return resultado.rowcount > 0


def bloquear_funcion(conexion, id_funcion: int) -> datetime:
    """
    Bloquea la funcion hasta el fin de la transaccion: las reservas de una misma
    funcion entran de a una, asi dos pedidos por la misma butaca no chocan en un
    deadlock y el segundo recibe el 409 de butaca ocupada.
    """
    return conexion.execute(
        text("""
            SELECT fecha_hora
            FROM funciones
            WHERE id_funcion = :id_funcion
            FOR UPDATE
        """),
        {'id_funcion': id_funcion},
    ).scalar()


def contar_butacas_de_sala(conexion, id_sala: int, butacas: list[int]) -> int:
    return conexion.execute(
        text("""
            SELECT COUNT(*)
            FROM butacas
            WHERE fk_id_sala = :id_sala
              AND id_butaca IN :butacas
        """).bindparams(bindparam('butacas', expanding=True)),
        {'id_sala': id_sala, 'butacas': butacas},
    ).scalar()


def liberar_reservas_vencidas(conexion, id_funcion: int, limite_reserva: datetime) -> None:
    """
    Pasa a vencidas las compras pendientes de la funcion creadas antes del limite
    y borra sus entradas, asi las butacas quedan libres.
    """
    parametros = {
        'id_funcion': id_funcion,
        'limite_reserva': limite_reserva,
        'estado_pendiente': ESTADO_PENDIENTE,
        'estado_vencida': ESTADO_VENCIDA,
    }
    conexion.execute(
        text("""
            DELETE e
            FROM entradas e
            JOIN compras c ON c.id_compra = e.fk_id_compra
            WHERE c.fk_id_funcion = :id_funcion
              AND c.estado = :estado_pendiente
              AND c.fecha_hora <= :limite_reserva
        """),
        parametros,
    )
    conexion.execute(
        text("""
            UPDATE compras
            SET estado = :estado_vencida
            WHERE fk_id_funcion = :id_funcion
              AND estado = :estado_pendiente
              AND fecha_hora <= :limite_reserva
        """),
        parametros,
    )


def insertar_compra(conexion, id_usuario: int, id_funcion: int, fecha_hora: datetime) -> int:
    resultado = conexion.execute(
        text("""
            INSERT INTO compras (fk_id_usuario, fk_id_funcion, estado, fecha_hora)
            VALUES (:id_usuario, :id_funcion, :estado_pendiente, :fecha_hora)
        """),
        {
            'id_usuario': id_usuario,
            'id_funcion': id_funcion,
            'estado_pendiente': ESTADO_PENDIENTE,
            'fecha_hora': fecha_hora,
        },
    )
    return resultado.lastrowid


def insertar_entradas(conexion, id_compra: int, id_funcion: int, butacas: list[int]) -> None:
    conexion.execute(
        text("""
            INSERT INTO entradas (fk_id_compra, fk_id_funcion, fk_id_butaca)
            VALUES (:id_compra, :id_funcion, :id_butaca)
        """),
        [
            {'id_compra': id_compra, 'id_funcion': id_funcion, 'id_butaca': id_butaca}
            for id_butaca in butacas
        ],
    )


def bloquear_compra(conexion, id_compra: int) -> dict | None:
    fila = conexion.execute(
        text("""
            SELECT id_compra, fk_id_usuario, estado
            FROM compras
            WHERE id_compra = :id_compra
            FOR UPDATE
        """),
        {'id_compra': id_compra},
    ).first()

    return fila_a_dict(fila) if fila is not None else None


def eliminar_compra(conexion, id_compra: int) -> None:
    """
    Borra la compra con sus servicios y entradas.
    """
    parametros = {'id_compra': id_compra}
    conexion.execute(text('DELETE FROM compras_servicios WHERE fk_id_compra = :id_compra'), parametros)
    conexion.execute(text('DELETE FROM entradas WHERE fk_id_compra = :id_compra'), parametros)
    conexion.execute(text('DELETE FROM compras WHERE id_compra = :id_compra'), parametros)
