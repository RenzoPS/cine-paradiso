from ..constants import GENERO_SIN_DEFINIR
from ..repositories import dashboard as db_dashboard
from ..utils import formatear_fecha_hora


def _porcentaje(vendidas: int, capacidad: int) -> float:
    if not capacidad:
        return 0.0

    return round(vendidas * 100 / capacidad, 1)


def _ocupacion_por_funcion(funciones: list[dict]) -> list[dict]:
    return [
        {
            'id_funcion': funcion['id_funcion'],
            'pelicula': funcion['pelicula'],
            'sala': funcion['sala'],
            'local': funcion['local'],
            'fecha_hora': formatear_fecha_hora(funcion['fecha_hora']),
            'vendidas': funcion['vendidas'],
            'capacidad': funcion['capacidad'],
            'porcentaje': _porcentaje(funcion['vendidas'], funcion['capacidad']),
        }
        for funcion in funciones
    ]


def _ocupacion_por_pelicula(funciones: list[dict]) -> list[dict]:
    peliculas = {}

    for funcion in funciones:
        pelicula = peliculas.setdefault(funcion['id_pelicula'], {
            'id_pelicula': funcion['id_pelicula'],
            'pelicula': funcion['pelicula'],
            'funciones': 0,
            'vendidas': 0,
            'capacidad': 0,
        })
        pelicula['funciones'] += 1
        pelicula['vendidas'] += funcion['vendidas']
        pelicula['capacidad'] += funcion['capacidad']

    for pelicula in peliculas.values():
        pelicula['porcentaje'] = _porcentaje(pelicula['vendidas'], pelicula['capacidad'])

    return sorted(peliculas.values(), key=lambda pelicula: pelicula['porcentaje'], reverse=True)


def _sumar_entradas_por(funciones: list[dict], clave, nombre: str) -> list[dict]:
    """
    Suma las entradas vendidas agrupando las funciones por la clave indicada y
    devuelve solo los grupos con ventas, de mayor a menor.
    """
    totales = {}

    for funcion in funciones:
        if funcion['vendidas']:
            grupo = clave(funcion)
            totales[grupo] = totales.get(grupo, 0) + funcion['vendidas']

    ordenados = sorted(totales.items(), key=lambda item: item[1], reverse=True)

    return [{nombre: grupo, 'entradas': entradas} for grupo, entradas in ordenados]


def _cancelaciones() -> dict:
    por_pelicula = db_dashboard.listar_cancelaciones_por_pelicula()

    return {
        'total': sum(pelicula['cancelaciones'] for pelicula in por_pelicula),
        'por_pelicula': por_pelicula,
    }


def obtener_dashboard() -> dict:
    """
    Arma los indicadores del backoffice. Una venta es una entrada de una compra
    pagada o usada: las pendientes son reservas sin pagar y no cuentan.
    """
    funciones = db_dashboard.listar_funciones_con_ventas()

    return {
        'ocupacion_por_funcion': _ocupacion_por_funcion(funciones),
        'ocupacion_por_pelicula': _ocupacion_por_pelicula(funciones),
        'ventas_por_genero': _sumar_entradas_por(
            funciones,
            lambda funcion: funcion['genero'] or GENERO_SIN_DEFINIR,
            'genero',
        ),
        'franjas_horarias': _sumar_entradas_por(
            funciones,
            lambda funcion: funcion['fecha_hora'].strftime('%H:00'),
            'hora',
        ),
        'cancelaciones': _cancelaciones(),
    }
