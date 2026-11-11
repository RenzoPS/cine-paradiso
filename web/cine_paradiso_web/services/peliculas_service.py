from cine_paradiso_web.services.api_service import llamar_api

COOKIE_SESION_API = 'token_sesion'


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


def buscar_peliculas_tmdb(consulta: str, token_sesion: str) -> dict:
    return llamar_api(
        'GET',
        'peliculas/tmdb',
        params={'q': consulta},
        cookies={COOKIE_SESION_API: token_sesion},
    )


def importar_pelicula(tmdb_id: int, token_sesion: str) -> dict:
    return llamar_api(
        'POST',
        'peliculas',
        json={'tmdb_id': tmdb_id},
        cookies={COOKIE_SESION_API: token_sesion},
    )


def actualizar_pelicula(
    id_pelicula: int,
    datos: dict,
    token_sesion: str,
) -> dict:
    return llamar_api(
        'PUT',
        f'peliculas/{id_pelicula}',
        json=datos,
        cookies={COOKIE_SESION_API: token_sesion},
    )


def eliminar_pelicula(id_pelicula: int, token_sesion: str) -> dict:
    return llamar_api(
        'DELETE',
        f'peliculas/{id_pelicula}',
        cookies={COOKIE_SESION_API: token_sesion},
    )
