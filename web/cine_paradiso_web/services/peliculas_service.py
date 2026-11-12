from cine_paradiso_web.services.api_service import llamar_api


def listar_peliculas(filtros: dict | None = None) -> dict:
    return llamar_api(
        'GET',
        'peliculas',
        params=filtros,
    )


def listar_todas_peliculas() -> dict:
    peliculas = []

    for activa in (True, False):
        offset = 0
        while True:
            respuesta = listar_peliculas({
                'activa': activa,
                '_limit': 100,
                '_offset': offset,
            })
            peliculas.extend(respuesta['peliculas'])
            offset += respuesta['_limit']
            if offset >= respuesta['_total']:
                break

    peliculas.sort(key=lambda pelicula: pelicula['id_pelicula'])
    return {'peliculas': peliculas}


def obtener_pelicula(id_pelicula: int) -> dict:
    return llamar_api(
        'GET',
        f'peliculas/{id_pelicula}',
    )


def buscar_peliculas_tmdb(consulta: str) -> dict:
    return llamar_api(
        'GET',
        'peliculas/tmdb',
        params={'q': consulta},
    )


def importar_pelicula(tmdb_id: int) -> dict:
    return llamar_api(
        'POST',
        'peliculas',
        json={'tmdb_id': tmdb_id},
    )


def actualizar_pelicula(
    id_pelicula: int,
    datos: dict,
) -> dict:
    return llamar_api(
        'PUT',
        f'peliculas/{id_pelicula}',
        json=datos,
    )


def eliminar_pelicula(id_pelicula: int) -> dict:
    return llamar_api(
        'DELETE',
        f'peliculas/{id_pelicula}',
    )
