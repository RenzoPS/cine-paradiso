from functools import wraps
from flask import request, current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from cine_paradiso_api.constants import (
    ERROR_CODE_AUTH_ACCESS_DENIED,
    ERROR_CODE_AUTH_TOKEN_EXPIRED,
    ERROR_CODE_AUTH_TOKEN_INVALID,
    ERROR_CODE_AUTH_TOKEN_MISSING,
    ROL_ADMIN,
    TOKEN_COOKIE_NOMBRE,
    TOKEN_DURACION_SEGUNDOS,
)
from cine_paradiso_api.utils import ErrorAPI

def _crear_serializador():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


def crear_token(id_usuario, rol):
    return _crear_serializador().dumps({'id_usuario': id_usuario, 'rol': rol})


def obtener_datos_token():
    token = request.cookies.get(TOKEN_COOKIE_NOMBRE)

    if not token:
        raise ErrorAPI(
            code=ERROR_CODE_AUTH_TOKEN_MISSING,
            message="Sesion no encontrada",
            description="Se requiere iniciar sesion para acceder a esta seccion.",
            status=401
        )

    try:
        return _crear_serializador().loads(token, max_age=TOKEN_DURACION_SEGUNDOS)
    except SignatureExpired:
        raise ErrorAPI(
            code=ERROR_CODE_AUTH_TOKEN_EXPIRED,
            message="Sesion expirada",
            description="Tu sesion ha expirado. Por favor, vuelve a iniciar sesion.",
            status=401
        )
    except BadSignature:
        raise ErrorAPI(
            code=ERROR_CODE_AUTH_TOKEN_INVALID,
            message="Sesion invalida",
            description="El token de sesion es invalido o ha sido manipulado.",
            status=401
        )


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        datos_usuario = obtener_datos_token()

        if datos_usuario.get('rol') != ROL_ADMIN:
            raise ErrorAPI(
                code=ERROR_CODE_AUTH_ACCESS_DENIED,
                message="Acceso denegado",
                description="No tienes los permisos de administrador requeridos para esta accion.",
                status=403
            )

        return f(*args, **kwargs)

    return decorated_function


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        obtener_datos_token()
        return f(*args, **kwargs)

    return decorated_function
