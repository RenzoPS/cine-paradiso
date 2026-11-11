from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from cine_paradiso_web.services.api_service import ApiError
from cine_paradiso_web.services.auth_service import admin_requerido
from cine_paradiso_web.services.peliculas_service import (
    actualizar_pelicula as guardar_pelicula,
    buscar_peliculas_tmdb as consultar_tmdb,
    eliminar_pelicula as dar_de_baja_pelicula,
    importar_pelicula as importar_desde_tmdb,
    listar_todas_peliculas,
    obtener_pelicula,
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
CAMPOS_EDITABLES_PELICULA = (
    'sinopsis',
    'poster_url',
    'clasificacion',
    'disponible_desde',
    'disponible_hasta',
)


def _datos_edicion_desde_formulario() -> dict:
    datos = {}
    for campo in CAMPOS_EDITABLES_PELICULA:
        valor = request.form.get(campo, '').strip()
        if campo in ('disponible_desde', 'disponible_hasta'):
            if valor:
                try:
                    fecha_hora = datetime.fromisoformat(valor)
                except ValueError as error:
                    raise ValueError(f"El campo '{campo}' no contiene una fecha válida.") from error
                if fecha_hora.tzinfo is not None:
                    raise ValueError(f"El campo '{campo}' debe usar la hora local del cine.")
                valor = fecha_hora.strftime('%Y-%m-%dT%H:%M:%S-03:00')
            else:
                valor = None
        else:
            valor = valor or None
        datos[campo] = valor
    return datos


@admin_bp.route('/', methods=['GET'])
@admin_bp.route('/dashboard', methods=['GET'])
@admin_requerido
def index():
    return render_template('admin/index.html')


@admin_bp.route('/peliculas', methods=['GET'])
@admin_requerido
def peliculas():
    try:
        respuesta = listar_todas_peliculas()
    except ApiError as error:
        flash(error.mensaje, 'error')
        peliculas = []
    else:
        peliculas = respuesta['peliculas']

    return render_template('admin/peliculas.html', peliculas=peliculas)


@admin_bp.route('/peliculas/tmdb', methods=['GET'])
@admin_requerido
def buscar_peliculas_tmdb():
    consulta = request.args.get('q', '').strip()
    resultados = []

    if consulta:
        token_sesion = session.get('token_sesion')
        if not token_sesion:
            flash('Iniciá sesión como administrador para buscar en TMDB.', 'warning')
        else:
            try:
                respuesta = consultar_tmdb(consulta, token_sesion)
            except ApiError as error:
                flash(error.mensaje, 'error')
            else:
                resultados = respuesta['resultados']

    return render_template(
        'admin/buscar_peliculas.html',
        consulta=consulta,
        resultados=resultados,
    )


@admin_bp.route('/peliculas/importar', methods=['POST'])
@admin_requerido
def importar_pelicula():
    consulta = request.form.get('q', '').strip()
    id_tmdb = request.form.get('tmdb_id', '').strip()
    token_sesion = session.get('token_sesion')

    if not token_sesion:
        flash('Iniciá sesión como administrador para importar películas.', 'warning')
        return redirect(url_for('admin.buscar_peliculas_tmdb', q=consulta))

    try:
        tmdb_id = int(id_tmdb)
    except ValueError:
        flash('El identificador de TMDB debe ser un número entero.', 'error')
        return redirect(url_for('admin.buscar_peliculas_tmdb', q=consulta))

    if tmdb_id < 1:
        flash('El identificador de TMDB debe ser positivo.', 'error')
        return redirect(url_for('admin.buscar_peliculas_tmdb', q=consulta))

    try:
        pelicula = importar_desde_tmdb(tmdb_id, token_sesion)
    except ApiError as error:
        flash(error.mensaje, 'error')
        return redirect(url_for('admin.buscar_peliculas_tmdb', q=consulta))

    flash(f"Se importó '{pelicula['titulo']}' al catálogo.", 'success')
    return redirect(url_for('admin.peliculas'))


@admin_bp.route('/peliculas/<int:id_pelicula>/editar', methods=['GET', 'POST'])
@admin_requerido
def editar_pelicula(id_pelicula):
    if request.method == 'POST':
        token_sesion = session.get('token_sesion')
        if not token_sesion:
            flash('Iniciá sesión como administrador para editar películas.', 'warning')
            return redirect(url_for('admin.editar_pelicula', id_pelicula=id_pelicula))

        try:
            datos = _datos_edicion_desde_formulario()
        except ValueError as error:
            flash(str(error), 'error')
            return redirect(url_for('admin.editar_pelicula', id_pelicula=id_pelicula))

        try:
            guardar_pelicula(id_pelicula, datos, token_sesion)
        except ApiError as error:
            flash(error.mensaje, 'error')
            return redirect(url_for('admin.editar_pelicula', id_pelicula=id_pelicula))

        flash('Los datos de la película se actualizaron correctamente.', 'success')
        return redirect(url_for('admin.peliculas'))

    try:
        pelicula = obtener_pelicula(id_pelicula)
    except ApiError as error:
        flash(error.mensaje, 'error')
        return redirect(url_for('admin.peliculas'))

    return render_template(
        'admin/editar_pelicula.html',
        id_pelicula=id_pelicula,
        pelicula=pelicula,
    )


@admin_bp.route('/peliculas/<int:id_pelicula>/baja', methods=['POST'])
@admin_requerido
def dar_de_baja(id_pelicula):
    token_sesion = session.get('token_sesion')
    if not token_sesion:
        flash('Iniciá sesión como administrador para dar de baja películas.', 'warning')
        return redirect(url_for('admin.peliculas'))

    try:
        dar_de_baja_pelicula(id_pelicula, token_sesion)
    except ApiError as error:
        flash(error.mensaje, 'error')
    else:
        flash('La película se dio de baja correctamente.', 'success')

    return redirect(url_for('admin.peliculas'))
