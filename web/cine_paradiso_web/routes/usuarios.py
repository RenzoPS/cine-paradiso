from flask import Blueprint, flash, make_response, redirect, render_template, session, url_for
import requests

from cine_paradiso_web.constants import TOKEN_COOKIE_NOMBRE
from cine_paradiso_web.seguridad import obtener_token
from cine_paradiso_web.services import usuarios as servicio_usuarios


usuarios_bp = Blueprint('usuarios', __name__)


@usuarios_bp.route('/mi-perfil', methods=['GET'])
def perfil():
    token = obtener_token()

    if not token:

        session.clear()
        return redirect(url_for('auth.login'))

    try:
        respuesta = servicio_usuarios.obtener_perfil(token)

        if respuesta.status_code == 200:
            datos_usuario = respuesta.json()
            return render_template('perfil.html', usuario=datos_usuario)

        if respuesta.status_code == 401:
            session.clear()
            
            respuesta_web = make_response(
                redirect(url_for('auth.login'))
            )
            respuesta_web.delete_cookie(TOKEN_COOKIE_NOMBRE)
            return respuesta_web

        if respuesta.status_code == 403:
            flash('No tenés permiso para acceder a esta sección.', 'error')
            return redirect(url_for('cartelera.listar'))

        flash('No fue posible obtener los datos del perfil.', 'error')
        return redirect(url_for('cartelera.listar'))

    except requests.exceptions.RequestException:
        flash('No fue posible conectar con el servidor.', 'error')
        return redirect(url_for('cartelera.listar'))
