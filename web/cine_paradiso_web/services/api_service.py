from typing import Any

import requests

from cine_paradiso_web.constants import API_URL

API_TIMEOUT = 5


class ApiError(Exception):
    def __init__(self, mensaje: str, status_code: int | None = None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.status_code = status_code


def llamar_api(
    metodo: str,
    ruta: str,
    *,
    params: dict | None = None,
    json: dict | None = None,
    cookies: dict[str, str] | None = None,
) -> Any:
    url = f'{API_URL.rstrip("/")}/{ruta.lstrip("/")}'

    try:
        respuesta = requests.request(
            metodo.upper(),
            url,
            params=params,
            json=json,
            cookies=cookies,
            timeout=API_TIMEOUT,
        )
    except requests.RequestException as error:
        raise ApiError('No se pudo conectar con la API.') from error

    if not respuesta.ok:
        mensaje = f'La API respondió con estado HTTP {respuesta.status_code}.'
        try:
            datos_error = respuesta.json()
        except ValueError:
            datos_error = None

        if isinstance(datos_error, dict):
            errores = datos_error.get('errors')
            if isinstance(errores, list) and errores and isinstance(errores[0], dict):
                partes = [
                    errores[0].get('message'),
                    errores[0].get('description'),
                ]
                mensaje = '. '.join(parte for parte in partes if parte) or mensaje

        raise ApiError(mensaje, respuesta.status_code)

    if respuesta.status_code == 204:
        return None

    try:
        return respuesta.json()
    except ValueError as error:
        raise ApiError(
            f'La API respondió con HTTP {respuesta.status_code}, pero no devolvió JSON válido.',
            respuesta.status_code,
        ) from error
