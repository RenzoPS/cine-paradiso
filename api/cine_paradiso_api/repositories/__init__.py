from contextlib import contextmanager

from flask import Flask, current_app
from sqlalchemy import create_engine, text

from ..constants import DB_URL


def init_app(app: Flask) -> None:
    app.extensions['motor'] = create_engine(DB_URL, pool_pre_ping=True)


def _motor():
    return current_app.extensions['motor']


def fila_a_dict(fila) -> dict:
    return dict(fila._mapping)


def ejecutar_consulta(sql: str, parametros: dict | None = None) -> list[dict]:
    with _motor().connect() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})

        return [fila_a_dict(fila) for fila in resultado]


def ejecutar_escalar(sql: str, parametros: dict | None = None):
    with _motor().connect() as conexion:
        return conexion.execute(text(sql), parametros or {}).scalar()


def ejecutar_mutacion(sql: str, parametros: dict | None = None) -> int:
    with _motor().begin() as conexion:
        resultado = conexion.execute(text(sql), parametros or {})

        return resultado.lastrowid or 0


@contextmanager
def transaccion():
    with _motor().begin() as conexion:
        yield conexion


def listar_paginado(tabla: str, filtros: dict, orden: str, limit: int, offset: int) -> tuple[list[dict], int]:
    # tabla y orden se interpolan: solo literales del código, nunca datos de la request
    condiciones = []
    parametros = {}

    for indice, (condicion, valor) in enumerate(filtros.items()):
        if valor is None:
            continue

        clave = f'f{indice}'
        condiciones.append(condicion.replace('?', f':{clave}'))
        parametros[clave] = valor

    where = ('WHERE ' + ' AND '.join(condiciones)) if condiciones else ''

    total = ejecutar_escalar(f'SELECT COUNT(*) FROM {tabla} {where}', parametros) or 0

    filas = ejecutar_consulta(
        f'SELECT * FROM {tabla} {where} ORDER BY {orden} LIMIT :_limit OFFSET :_offset',
        {**parametros, '_limit': limit, '_offset': offset},
    )

    return filas, total
