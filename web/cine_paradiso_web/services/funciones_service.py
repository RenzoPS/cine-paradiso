from cine_paradiso_web.services.api_service import llamar_api


def listar_funciones(filtros: dict | None = None) -> dict:
    return llamar_api(
        'GET',
        'funciones',
        params=filtros,
    )


def listar_todas_funciones(filtros: dict | None = None) -> dict:
    parametros = dict(filtros or {})
    parametros.update({'_limit': 100, '_offset': 0})
    respuesta = listar_funciones(parametros)
    funciones = list(respuesta['funciones'])

    for offset in range(respuesta['_limit'], respuesta['_total'], respuesta['_limit']):
        pagina = listar_funciones({
            **parametros,
            '_limit': respuesta['_limit'],
            '_offset': offset,
        })
        funciones.extend(pagina['funciones'])

    return {'funciones': funciones}


def obtener_funcion(id_funcion: int) -> dict:
    return llamar_api(
        'GET',
        f'funciones/{id_funcion}',
    )


def listar_salas() -> dict:
    return llamar_api(
        'GET',
        'salas',
    )


def crear_funcion(datos: dict) -> dict:
    return llamar_api(
        'POST',
        'funciones',
        json=datos,
    )


def actualizar_funcion(id_funcion: int, datos: dict) -> dict:
    return llamar_api(
        'PUT',
        f'funciones/{id_funcion}',
        json=datos,
    )


def eliminar_funcion(id_funcion: int) -> None:
    llamar_api(
        'DELETE',
        f'funciones/{id_funcion}',
    )
