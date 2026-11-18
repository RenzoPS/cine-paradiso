from datetime import date, timedelta

from cine_paradiso_web.services.api_service import llamar_api, ApiError


def obtener_peliculas_cartelera(sucursal=None, fecha=None, genero=None, busqueda=None):
    """
    Consume GET {API_URL}/peliculas enviando los filtros correspondientes a la cartelera.
    Retorna una lista de películas. En caso de error o falla de conexión, retorna lista vacía.
    """
    parametros = {'en_cartel': 'true'}

    if sucursal:
        parametros['id_local'] = str(sucursal).strip()

    if fecha:
        fecha_str = str(fecha).strip().lower()
        hoy = date.today()

        if fecha_str == 'hoy':
            parametros['fecha'] = hoy.isoformat()
        elif fecha_str == 'manana':
            parametros['fecha'] = (hoy + timedelta(days=1)).isoformat()
        elif fecha_str != 'todos' and fecha_str != 'finde':
            parametros['fecha'] = fecha_str

    if genero and genero != 'Todos':
        parametros['genero'] = str(genero).strip()

    if busqueda and str(busqueda).strip():
        parametros['titulo'] = str(busqueda).strip()

    try:
        datos = llamar_api(
            'GET',
            'peliculas',
            params=parametros,
        )
    except ApiError:
        return []

    if isinstance(datos, dict):
        return datos.get('peliculas', [])

    if isinstance(datos, list):
        return datos

    return []


def obtener_pelicula_por_id(id_pelicula):
    """
    Consume GET {API_URL}/peliculas/{id_pelicula}.
    Si responde 404 o falla la conexión, retorna None.
    """
    try:
        return llamar_api(
            'GET',
            f'peliculas/{id_pelicula}',
        )
    except ApiError:
        return None
