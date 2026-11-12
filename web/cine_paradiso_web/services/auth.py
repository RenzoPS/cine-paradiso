
import requests

from cine_paradiso_web.constants import API_URL


def registrar_usuario(datos):
    return requests.post(
        f'{API_URL}/auth/registro',
        json=datos,
        timeout=5
    )


def iniciar_sesion(datos):
    return requests.post(
        f'{API_URL}/auth/login',
        json=datos,
        timeout=5
    )
