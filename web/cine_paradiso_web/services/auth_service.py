from functools import wraps
from flask import current_app, flash, redirect, session, url_for

from cine_paradiso_web.services.api_service import ApiError, llamar_api


def iniciar_sesion(email: str, contrasena: str) -> dict:
    resultado = llamar_api(
        'POST',
        'auth/login',
        json={'email': email, 'contrasena': contrasena},
    )

    if (
        not isinstance(resultado, dict)
        or not isinstance(resultado.get('token'), str)
        or not resultado['token']
        or not isinstance(resultado.get('id_usuario'), int)
        or resultado.get('rol') not in ('admin', 'cliente')
    ):
        raise ApiError('La API devolvió una respuesta de inicio de sesión inválida.')

    return resultado


def admin_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        usuario = session.get('usuario')
        if not usuario:
            flash('Debes iniciar sesión para acceder al backoffice.', 'warning')
            url_login = 'auth.login' if 'auth.login' in current_app.view_functions else 'cartelera.listar'
            return redirect(url_for(url_login))

        if usuario.get('rol') != 'admin':
            flash('Acceso denegado: se requieren permisos de administrador.', 'error')
            return redirect(url_for('cartelera.listar'))

        return f(*args, **kwargs)

    return decorated_function
