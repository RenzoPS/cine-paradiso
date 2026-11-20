import requests

from cine_paradiso_web.constants import API_URL, TOKEN_COOKIE_NOMBRE


def obtener_perfil(token):
    return requests.get(
        f'{API_URL}/usuarios/me',
        cookies={TOKEN_COOKIE_NOMBRE: token},
        timeout=5
    )
