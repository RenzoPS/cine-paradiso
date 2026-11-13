from flask import flash, request, make_response, redirect, session, url_for

from cine_paradiso_web.constants import ROL_ADMIN, TOKEN_COOKIE_NOMBRE


def obtener_token():
    return request.cookies.get(TOKEN_COOKIE_NOMBRE)


def verificar_autenticacion():
    token = obtener_token()

    if not token:
        return False

    return True


def redirigir_al_login():
    respuesta = make_response(
        redirect(url_for('auth.login'))
    )

    respuesta.delete_cookie(TOKEN_COOKIE_NOMBRE)

    return respuesta


def verificar_administrador():
    usuario = session.get('usuario')

    if not usuario or not verificar_autenticacion():
        flash('Debes iniciar sesión para acceder al backoffice.', 'warning')
        return redirigir_al_login()

    if usuario.get('rol') != ROL_ADMIN:
        flash('Acceso denegado: se requieren permisos de administrador.', 'error')
        return redirect(url_for('cartelera.listar'))

    return None
