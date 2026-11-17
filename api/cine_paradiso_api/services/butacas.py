from ..repositories import butacas as db_butacas
from .compras import vencer_reservas_de_funcion
from .funciones import buscar_funcion


def obtener_mapa_butacas(id_funcion) -> dict:
    funcion = buscar_funcion(id_funcion)
    vencer_reservas_de_funcion(funcion['id_funcion'])
    butacas = db_butacas.listar_butacas_de_funcion(funcion['id_funcion'], funcion['id_sala'])

    filas = []
    for butaca in butacas:
        if not filas or filas[-1]['fila'] != butaca['fila']:
            filas.append({'fila': butaca['fila'], 'butacas': []})
        filas[-1]['butacas'].append({
            'id_butaca': butaca['id_butaca'],
            'numero': butaca['numero'],
            'ocupada': bool(butaca['ocupada']),
        })

    ocupadas = sum(1 for butaca in butacas if butaca['ocupada'])

    return {
        'funcion': funcion,
        'capacidad': len(butacas),
        'disponibles': len(butacas) - ocupadas,
        'filas': filas,
    }
