from cine_paradiso_web.services.api_service import llamar_api


def listar_servicios(activo: bool = True) -> dict:
    return llamar_api(
        'GET',
        'servicios',
        params={'activo': 'true' if activo else 'false', '_limit': 100, '_offset': 0},
    )


def listar_todos_servicios() -> dict:
    servicios = []

    for activo in (True, False):
        servicios.extend(listar_servicios(activo)['servicios'])

    servicios.sort(key=lambda servicio: servicio['id_servicio'])
    return {'servicios': servicios}


def obtener_servicio(id_servicio: int) -> dict:
    return llamar_api('GET', f'servicios/{id_servicio}')


def crear_servicio(datos: dict) -> dict:
    return llamar_api('POST', 'servicios', json=datos)


def actualizar_servicio(id_servicio: int, datos: dict) -> dict:
    return llamar_api('PUT', f'servicios/{id_servicio}', json=datos)


def dar_de_baja_servicio(id_servicio: int) -> dict:
    return llamar_api('DELETE', f'servicios/{id_servicio}')


def dar_de_alta_servicio(id_servicio: int) -> dict:
    servicio = obtener_servicio(id_servicio)

    return actualizar_servicio(id_servicio, {
        'nombre': servicio['nombre'],
        'descripcion': servicio['descripcion'],
        'precio': servicio['precio'],
        'activo': True,
    })


def obtener_servicios_de_compra(id_compra: int) -> dict:
    return llamar_api('GET', f'compras/{id_compra}/servicios')


def guardar_servicios_de_compra(id_compra: int, items: list[dict]) -> dict:
    return llamar_api('PUT', f'compras/{id_compra}/servicios', json={'servicios': items})
