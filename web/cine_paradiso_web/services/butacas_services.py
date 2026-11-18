from cine_paradiso_web.services.api_service import llamar_api

def obtener_mapa_butacas(id_funcion: int) -> dict:
    return llamar_api(
        'GET',
        f'funciones/{id_funcion}/butacas',
    )


def crear_compra_butacas(id_funcion: int, butacas: list[int]) -> dict:
    return llamar_api(
        'POST',
        'compras',
        json={
            'id_funcion': id_funcion,
            'butacas': butacas,
        },
    )
