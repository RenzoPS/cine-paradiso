from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from cine_paradiso_api.constants import (
    ERROR_CODE_AUTH_CREDENCIALES_INVALIDAS,
    ERROR_CODE_USUARIO_EMAIL_DUPLICADO,
    ROL_CLIENTE,
    TOKEN_DURACION_SEGUNDOS,
    TZ_ARG,
)
from cine_paradiso_api.repositories import usuarios as repositorio_usuarios
from cine_paradiso_api.seguridad import crear_token
from cine_paradiso_api.utils import ErrorAPI, formatear_fecha_hora


def registrar_usuario(datos):
    if repositorio_usuarios.obtener_usuario_por_email(datos['email']):
        raise ErrorAPI(
            code=ERROR_CODE_USUARIO_EMAIL_DUPLICADO,
            message='Email ya registrado',
            description=f"Ya existe un usuario con el email '{datos['email']}'",
            status=409
        )

    
    fecha_creacion = datetime.now(TZ_ARG).replace(tzinfo=None)
    id_usuario = repositorio_usuarios.insertar_usuario(
        datos['nombre'],
        datos['apellido'],
        datos['email'],
        generate_password_hash(datos['contrasena']),
        ROL_CLIENTE,
        fecha_creacion,
    )

    return {
        'id_usuario': id_usuario,
        'nombre': datos['nombre'],
        'apellido': datos['apellido'],
        'email': datos['email'],
        'rol': ROL_CLIENTE,
        'fecha_creacion': formatear_fecha_hora(fecha_creacion),
    }


def iniciar_sesion(datos):
    usuario = repositorio_usuarios.obtener_usuario_por_email(datos['email'])

  
    if not usuario or not check_password_hash(usuario['contrasena_hash'], datos['contrasena']):
        raise ErrorAPI(
            code=ERROR_CODE_AUTH_CREDENCIALES_INVALIDAS,
            message='Credenciales invalidas',
            description='El email o la contrasena son incorrectos',
            status=401
        )

    return {
        'token': crear_token(usuario['id_usuario'], usuario['rol']),
        'id_usuario': usuario['id_usuario'],
        'rol': usuario['rol'],
        'expira_en_segundos': TOKEN_DURACION_SEGUNDOS,
    }
