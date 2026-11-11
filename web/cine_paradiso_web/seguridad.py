from flask import request, make_response, redirect, url_for


def obtener_token():
    return request.cookies.get('token_sesion')


def verificar_autenticacion():
    token = obtener_token()

    if not token:
        return False

    return True


def redirigir_al_login():
    respuesta = make_response(
        redirect(url_for('auth.login'))
    )

    respuesta.delete_cookie('token_sesion')

    return respuesta
