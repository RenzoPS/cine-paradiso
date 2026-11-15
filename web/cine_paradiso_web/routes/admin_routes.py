from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from cine_paradiso_web.seguridad import verificar_administrador
from cine_paradiso_web.services.api_service import ApiError
from cine_paradiso_web.services.peliculas_service import (
    actualizar_pelicula as guardar_pelicula,
    buscar_peliculas_tmdb as consultar_tmdb,
    eliminar_pelicula as dar_de_baja_pelicula,
    importar_pelicula as importar_desde_tmdb,
    listar_todas_peliculas,
    obtener_pelicula,
)
from cine_paradiso_web.services.funciones_service import (
    actualizar_funcion as guardar_funcion,
    crear_funcion as programar_funcion,
    eliminar_funcion as eliminar_funcion_api,
    listar_salas,
    listar_todas_funciones,
    obtener_funcion,
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


def _datos_funcion_desde_formulario() -> dict:
    valor_fecha = request.form.get('fecha_hora', '').strip()
    try:
        fecha_hora = datetime.fromisoformat(valor_fecha)
    except ValueError as error:
        raise ValueError("El campo 'fecha_hora' no contiene una fecha válida.") from error

    if fecha_hora.tzinfo is not None:
        raise ValueError("El campo 'fecha_hora' debe usar la hora local del cine.")

    return {
        'id_pelicula': request.form.get('id_pelicula', '').strip(),
        'id_sala': request.form.get('id_sala', '').strip(),
        'fecha_hora': fecha_hora.strftime('%Y-%m-%dT%H:%M:%S-03:00'),
        'precio': request.form.get('precio', '').strip(),
    }


def _leer_id_local(valor: str | None) -> int | None:
    if not valor:
        return None

    try:
        id_local = int(valor)
    except ValueError as error:
        raise ValueError('El local seleccionado no es válido.') from error

    if id_local < 1:
        raise ValueError('El local seleccionado no es válido.')

    return id_local


def _opciones_funcion() -> tuple[list[dict], list[dict], list[dict]]:
    peliculas = [
        pelicula
        for pelicula in listar_todas_peliculas()['peliculas']
        if pelicula['activa']
        and pelicula['duracion_min']
        and pelicula['disponible_desde']
        and pelicula['disponible_hasta']
    ]
    salas_disponibles = listar_salas()['salas']
    locales = []
    locales_vistos = set()
    for sala in salas_disponibles:
        if sala['id_local'] not in locales_vistos:
            locales.append({
                'id_local': sala['id_local'],
                'local': sala['local'],
                'direccion': sala['direccion'],
            })
            locales_vistos.add(sala['id_local'])

    return peliculas, locales, salas_disponibles


@admin_bp.route('/', methods=['GET'])
def index():
    redireccion = verificar_administrador()
    if redireccion:
        return redireccion

    return render_template('admin/index.html')


@admin_bp.route('/dashboard', methods=['GET'])
def dashboard():
    redireccion = verificar_administrador()
    if redireccion:
        return redireccion

    return render_template('admin/dashboard.html')


@admin_bp.route('/peliculas', methods=['GET'])
def peliculas():
    redireccion = verificar_administrador()
    if redireccion:
        return redireccion

    try:
        respuesta = listar_todas_peliculas()
    except ApiError as error:
        flash(error.mensaje, 'error')
        peliculas = []
    else:
        peliculas = respuesta['peliculas']

    return render_template('admin/peliculas.html', peliculas=peliculas)


@admin_bp.route('/peliculas/tmdb', methods=['GET'])
def buscar_peliculas_tmdb():
    redireccion = verificar_administrador()
    if redireccion:
        return redireccion

    consulta = request.args.get('q', '').strip()
    resultados = []

    if consulta:
        try:
            respuesta = consultar_tmdb(consulta)
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
def importar_pelicula():
    redireccion = verificar_administrador()
    if redireccion:
        return redireccion

    consulta = request.form.get('q', '').strip()
    id_tmdb = request.form.get('tmdb_id', '').strip()

    try:
        tmdb_id = int(id_tmdb)
    except ValueError:
        flash('El identificador de TMDB debe ser un número entero.', 'error')
        return redirect(url_for('admin.buscar_peliculas_tmdb', q=consulta))

    if tmdb_id < 1:
        flash('El identificador de TMDB debe ser positivo.', 'error')
        return redirect(url_for('admin.buscar_peliculas_tmdb', q=consulta))

    try:
        pelicula = importar_desde_tmdb(tmdb_id)
    except ApiError as error:
        flash(error.mensaje, 'error')
        return redirect(url_for('admin.buscar_peliculas_tmdb', q=consulta))

    flash(f"Se importó '{pelicula['titulo']}' al catálogo.", 'success')
    return redirect(url_for('admin.peliculas'))


@admin_bp.route('/peliculas/<int:id_pelicula>/editar', methods=['GET', 'POST'])
def editar_pelicula(id_pelicula):
    redireccion = verificar_administrador()
    if redireccion:
        return redireccion

    if request.method == 'POST':
        try:
            datos = _datos_edicion_desde_formulario()
        except ValueError as error:
            flash(str(error), 'error')
            return redirect(url_for('admin.editar_pelicula', id_pelicula=id_pelicula))

        try:
            guardar_pelicula(id_pelicula, datos)
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
def dar_de_baja(id_pelicula):
    redireccion = verificar_administrador()
    if redireccion:
        return redireccion

    try:
        dar_de_baja_pelicula(id_pelicula)
    except ApiError as error:
        flash(error.mensaje, 'error')
    else:
        flash('La película se dio de baja correctamente.', 'success')

    return redirect(url_for('admin.peliculas'))


@admin_bp.route('/funciones', methods=['GET'])
def funciones():
    redireccion = verificar_administrador()
    if redireccion:
        return redireccion

    try:
        respuesta = listar_todas_funciones()
    except ApiError as error:
        flash(error.mensaje, 'error')
        funciones_disponibles = []
    else:
        funciones_disponibles = respuesta['funciones']

    return render_template(
        'admin/funciones.html',
        funciones=funciones_disponibles,
    )


@admin_bp.route('/funciones/nueva', methods=['GET', 'POST'])
def nueva_funcion():
    redireccion = verificar_administrador()
    if redireccion:
        return redireccion

    if request.method == 'POST':
        try:
            datos = _datos_funcion_desde_formulario()
        except ValueError as error:
            flash(str(error), 'error')
            return redirect(url_for(
                'admin.nueva_funcion',
                id_local=request.form.get('id_local', ''),
            ))

        try:
            programar_funcion(datos)
        except ApiError as error:
            flash(error.mensaje, 'error')
            return redirect(url_for(
                'admin.nueva_funcion',
                id_local=request.form.get('id_local', ''),
            ))

        flash('La función se programó correctamente.', 'success')
        return redirect(url_for('admin.funciones'))

    try:
        id_local = _leer_id_local(request.args.get('id_local'))
        peliculas, locales, salas = _opciones_funcion()
    except ValueError as error:
        flash(str(error), 'error')
        return redirect(url_for('admin.nueva_funcion'))
    except ApiError as error:
        flash(error.mensaje, 'error')
        return redirect(url_for('admin.funciones'))

    return render_template(
        'admin/editar_funcion.html',
        funcion=None,
        peliculas=peliculas,
        locales=locales,
        salas=salas,
        id_local=id_local,
    )


@admin_bp.route('/funciones/<int:id_funcion>/editar', methods=['GET', 'POST'])
def editar_funcion(id_funcion):
    redireccion = verificar_administrador()
    if redireccion:
        return redireccion

    if request.method == 'POST':
        try:
            datos = _datos_funcion_desde_formulario()
        except ValueError as error:
            flash(str(error), 'error')
            return redirect(url_for(
                'admin.editar_funcion',
                id_funcion=id_funcion,
                id_local=request.form.get('id_local', ''),
            ))

        try:
            guardar_funcion(id_funcion, datos)
        except ApiError as error:
            flash(error.mensaje, 'error')
            return redirect(url_for(
                'admin.editar_funcion',
                id_funcion=id_funcion,
                id_local=request.form.get('id_local', ''),
            ))

        flash('La función se actualizó correctamente.', 'success')
        return redirect(url_for('admin.funciones'))

    try:
        funcion = obtener_funcion(id_funcion)
        id_local = _leer_id_local(request.args.get('id_local')) or funcion['id_local']
        peliculas, locales, salas = _opciones_funcion()
    except ValueError as error:
        flash(str(error), 'error')
        return redirect(url_for('admin.editar_funcion', id_funcion=id_funcion))
    except ApiError as error:
        flash(error.mensaje, 'error')
        return redirect(url_for('admin.funciones'))

    return render_template(
        'admin/editar_funcion.html',
        funcion=funcion,
        peliculas=peliculas,
        locales=locales,
        salas=salas,
        id_local=id_local,
    )


@admin_bp.route('/funciones/<int:id_funcion>/baja', methods=['POST'])
def dar_de_baja_funcion(id_funcion):
    redireccion = verificar_administrador()
    if redireccion:
        return redireccion

    try:
        eliminar_funcion_api(id_funcion)
    except ApiError as error:
        flash(error.mensaje, 'error')
    else:
        flash('La función se dio de baja correctamente.', 'success')

    return redirect(url_for('admin.funciones'))
