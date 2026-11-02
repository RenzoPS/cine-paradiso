from datetime import datetime

from sqlalchemy import text

from ..constants import ESTADO_PAGADA, ESTADO_PENDIENTE
from . import ejecutar_consulta, transaccion

def obtener_compra_por_id(id_compra: int) -> dict:
    """
    Busca una compra por su ID. Devuelve {} si no existe.
    """
    sql = """
        SELECT id_compra, fk_id_usuario, fk_id_funcion, estado, total, numero_factura, fecha_vencimiento, fecha_pago
        FROM compras
        WHERE id_compra = :id_compra
    """
    filas = ejecutar_consulta(sql, {'id_compra': id_compra})
    return filas[0] if filas else {}


def obtener_entradas_de_compra(id_compra: int) -> list[dict]:
    """
    Entradas de una compra, con la fila y el numero de cada butaca.
    """
    sql = """
        SELECT b.fila, b.numero, e.precio_unitario
        FROM entradas e
        JOIN butacas b ON b.id_butaca = e.fk_id_butaca
        WHERE e.fk_id_compra = :id_compra
        ORDER BY b.fila, b.numero
    """
    return ejecutar_consulta(sql, {'id_compra': id_compra})


def obtener_servicios_de_compra(id_compra: int) -> list[dict]:
    """
    Servicios de una compra, con el precio que tenian al comprarse.
    """
    sql = """
        SELECT s.nombre, cs.cantidad, cs.precio_unitario
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


def actualizar_compra_pagada(id_compra: int, numero_factura: str, fecha_pago: datetime) -> bool:
    """
    Pasa la compra de pendiente a pagada y calcula el total (entradas mas servicios) en la misma sentencia. Devuelve False si no cambio nada porque la compra ya no estaba pendiente.
    """
    sql = """
        UPDATE compras
        SET estado = :estado_pagada,
            numero_factura = :numero_factura,
            fecha_pago = :fecha_pago,
            total = (
                SELECT COALESCE(SUM(precio_unitario), 0)
                FROM entradas 
                WHERE fk_id_compra = :id_compra
            ) + (
                SELECT COALESCE(SUM(cantidad * precio_unitario), 0)
                FROM compras_servicios WHERE fk_id_compra = :id_compra
            )
        WHERE id_compra = :id_compra
            AND estado = :estado_pendiente
    """
    with transaccion() as conexion:
        resultado = conexion.execute(text(sql), {
            'id_compra': id_compra,
            'numero_factura': numero_factura,
            'fecha_pago': fecha_pago,
            'estado_pagada': ESTADO_PAGADA,
            'estado_pendiente': ESTADO_PENDIENTE,
        })
        return resultado.rowcount > 0