from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from cine_paradiso_web.services.api_service import ApiError
from cine_paradiso_web.services.auth_service import iniciar_sesion

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')

    email = request.form.get('email', '').strip()
    contrasena = request.form.get('contrasena', '')

    try:
        resultado = iniciar_sesion(email, contrasena)
    except ApiError as error:
        flash(error.mensaje, 'error')
        return render_template('auth/login.html', email=email)

    session.clear()
    session['usuario'] = {
        'id_usuario': resultado['id_usuario'],
        'email': email,
        'rol': resultado['rol'],
    }
    session['token_sesion'] = resultado['token']

    flash('Iniciaste sesión correctamente.', 'success')
    if resultado['rol'] == 'admin':
        return redirect(url_for('admin.index'))
    return redirect(url_for('cartelera.listar'))


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('Cerraste sesión.', 'success')
    return redirect(url_for('cartelera.listar'))
