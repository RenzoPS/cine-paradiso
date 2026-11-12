from datetime import date, timedelta
import requests

from cine_paradiso_web.constants import API_TIMEOUT_SEGUNDOS, API_URL


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
            # Si viene directamente en formato YYYY-MM-DD
            parametros['fecha'] = fecha_str

    if genero and genero != 'Todos':
        parametros['genero'] = str(genero).strip()

    if busqueda and str(busqueda).strip():
        parametros['titulo'] = str(busqueda).strip()

    try:
        respuesta = requests.get(
            f'{API_URL}/peliculas',
            params=parametros,
            timeout=API_TIMEOUT_SEGUNDOS,
        )
    except requests.RequestException:
        return []

    if not respuesta.ok:
        return []

    try:
        datos = respuesta.json()
        if isinstance(datos, dict):
            return datos.get('peliculas', [])
        if isinstance(datos, list):
            return datos
        return []
    except (ValueError, KeyError):
        return []


def obtener_pelicula_por_id(id_pelicula):
    """
    Consume GET {API_URL}/peliculas/{id_pelicula}.
    Si responde 404 o falla la conexión, retorna None.
    """
    try:
        respuesta = requests.get(
            f'{API_URL}/peliculas/{id_pelicula}',
            timeout=API_TIMEOUT_SEGUNDOS,
        )
    except requests.RequestException:
        return None

    if respuesta.status_code == 404 or not respuesta.ok:
        return None

    try:
        return respuesta.json()
    except ValueError:
        return None
