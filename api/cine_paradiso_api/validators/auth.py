from cine_paradiso_api.constants import (
    APELLIDO_MAX_LARGO,
    CAMPOS_LOGIN,
    CAMPOS_REGISTRO,
    CONTRASENA_MAX_LARGO,
    CONTRASENA_MIN_LARGO,
    EMAIL_MAX_LARGO,
    NOMBRE_MAX_LARGO,
)
from cine_paradiso_api.utils import (
    rechazar_campos_desconocidos,
    validar_cuerpo_no_vacio,
    validar_email,
    validar_maximo,
    validar_minimo,
    validar_string_no_vacio,
)


def _validar_texto(body, campo, largo_maximo):
    texto = validar_string_no_vacio(body.get(campo), campo)
    validar_maximo(len(texto), largo_maximo, campo)
    return texto


def _validar_contrasena(body):
    contrasena = body.get('contrasena')
    validar_string_no_vacio(contrasena, 'contrasena')
    return contrasena


def validar_registro(body):
    body = validar_cuerpo_no_vacio(body)
    rechazar_campos_desconocidos(body, CAMPOS_REGISTRO)

    email = validar_email(body.get('email'))
    validar_maximo(len(email), EMAIL_MAX_LARGO, 'email')

    contrasena = _validar_contrasena(body)
    validar_minimo(len(contrasena), CONTRASENA_MIN_LARGO, 'contrasena')
    validar_maximo(len(contrasena), CONTRASENA_MAX_LARGO, 'contrasena')

    return {
        'nombre': _validar_texto(body, 'nombre', NOMBRE_MAX_LARGO),
        'apellido': _validar_texto(body, 'apellido', APELLIDO_MAX_LARGO),
        'email': email,
        'contrasena': contrasena,
    }


def validar_login(body):
    body = validar_cuerpo_no_vacio(body)
    rechazar_campos_desconocidos(body, CAMPOS_LOGIN)

    return {
        'email': validar_email(body.get('email')),
        'contrasena': _validar_contrasena(body),
    }
