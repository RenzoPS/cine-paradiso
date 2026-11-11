import requests

from cine_paradiso_web.constants import API_URL


def obtener_perfil(token):
    return requests.get(
        f'{API_URL}/usuarios/me',
        cookies={'token_sesion': token},
        timeout=5
    )
