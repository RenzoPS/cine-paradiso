from flask import Blueprint, flash, make_response, redirect, render_template, request, session, url_for
import requests

from cine_paradiso_web.constants import TOKEN_COOKIE_NOMBRE
from cine_paradiso_web.services import auth as servicio_auth
from cine_paradiso_web.services import usuarios as servicio_usuarios


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():

    if request.method == 'POST':
        datos = {
            'nombre': request.form.get('nombre', '').strip(),
            'apellido': request.form.get('apellido', '').strip(),
            'email': request.form.get('email', '').strip(),
            'contrasena': request.form.get('contrasena', '')
        }

        try:
            respuesta = servicio_auth.registrar_usuario(datos)

            if respuesta.status_code == 201:
                flash('Tu cuenta fue creada correctamente. Ya puedes iniciar sesión.', 'success')
                return redirect(url_for('auth.login'))

            flash('No se pudo completar el registro. Revisa los datos e intenta nuevamente.', 'error')

        except requests.exceptions.RequestException:
            flash('No fue posible conectar con el servidor. Intenta nuevamente más tarde.', 'error')

    return render_template('registro.html')



@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        datos = {
            'email': request.form.get('email', '').strip(),
            'contrasena': request.form.get('contrasena', '')
        }

        try:
            respuesta = servicio_auth.iniciar_sesion(datos)

            if respuesta.status_code == 200:
                token = respuesta.cookies.get(TOKEN_COOKIE_NOMBRE)

                if not token:
                    flash('No se pudo obtener el token de autenticación.', 'error')
                    return redirect(url_for('auth.login'))

                respuesta_perfil = servicio_usuarios.obtener_perfil(token)

                if respuesta_perfil.status_code != 200:
                    flash('No se pudieron obtener los datos del usuario.', 'error')
                    return redirect(url_for('auth.login'))

                session['usuario'] = respuesta_perfil.json()

                respuesta_web = make_response(
                    redirect(url_for('cartelera.listar'))
                )

                respuesta_web.set_cookie(
                    TOKEN_COOKIE_NOMBRE,
                    token,
                    max_age=86400,
                    httponly=True,
                    samesite='Lax',
                    secure=False
                )

                return respuesta_web

            flash('Correo electrónico o contraseña incorrectos.', 'error')

        except requests.exceptions.RequestException:
            flash('No fue posible conectar con el servidor. Intentá nuevamente más tarde.', 'error')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()

    respuesta = make_response(
        redirect(url_for('cartelera.listar'))
    )

    respuesta.delete_cookie(TOKEN_COOKIE_NOMBRE)

    return respuesta
