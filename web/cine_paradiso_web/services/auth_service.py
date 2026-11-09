from functools import wraps
from flask import current_app, flash, redirect, session, url_for


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
