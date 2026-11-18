from flask import Blueprint, flash, redirect, render_template, request, url_for

from cine_paradiso_web.seguridad import redirigir_al_login, verificar_administrador, verificar_autenticacion
from cine_paradiso_web.services.api_service import ApiError
from cine_paradiso_web.services.servicios_service import (
    actualizar_servicio,
    crear_servicio,
    dar_de_alta_servicio,
    dar_de_baja_servicio,
    guardar_servicios_de_compra,
    listar_servicios,
    listar_todos_servicios,
    obtener_servicio,
    obtener_servicios_de_compra,
)

servicios_admin_bp = Blueprint('servicios_admin', __name__, url_prefix='/admin/servicios')
servicios_bp = Blueprint('servicios', __name__)


def _datos_servicio_desde_formulario() -> dict:
    return {
        'nombre': request.form.get('nombre', '').strip(),
        'descripcion': request.form.get('descripcion', '').strip() or None,
        'precio': request.form.get('precio', '').strip(),
        'activo': request.form.get('activo') == 'on',
    }


@servicios_admin_bp.route('/', methods=['GET'])
def listar():
    redireccion = verificar_administrador()
    if redireccion:
        return redireccion

    try:
        servicios = listar_todos_servicios()['servicios']
    except ApiError as error:
        flash(error.mensaje, 'error')
        servicios = []

    return render_template('admin/servicios.html', servicios=servicios)


@servicios_admin_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    redireccion = verificar_administrador()
    if redireccion:
        return redireccion

    if request.method == 'POST':
        datos = _datos_servicio_desde_formulario()

        try:
            crear_servicio(datos)
        except ApiError as error:
            flash(error.mensaje, 'error')
            return render_template('admin/servicio_form.html', servicio=datos, id_servicio=None)

        flash('El servicio se creó correctamente.', 'success')
        return redirect(url_for('servicios_admin.listar'))

    return render_template('admin/servicio_form.html', servicio=None, id_servicio=None)


@servicios_admin_bp.route('/<int:id_servicio>/editar', methods=['GET', 'POST'])
def editar(id_servicio):
    redireccion = verificar_administrador()
    if redireccion:
        return redireccion

    if request.method == 'POST':
        datos = _datos_servicio_desde_formulario()

        try:
            actualizar_servicio(id_servicio, datos)
        except ApiError as error:
            flash(error.mensaje, 'error')
            return render_template('admin/servicio_form.html', servicio=datos, id_servicio=id_servicio)

        flash('El servicio se actualizó correctamente.', 'success')
        return redirect(url_for('servicios_admin.listar'))

    try:
        servicio = obtener_servicio(id_servicio)
    except ApiError as error:
        flash(error.mensaje, 'error')
        return redirect(url_for('servicios_admin.listar'))

    return render_template('admin/servicio_form.html', servicio=servicio, id_servicio=id_servicio)


@servicios_admin_bp.route('/<int:id_servicio>/baja', methods=['POST'])
def baja(id_servicio):
    redireccion = verificar_administrador()
    if redireccion:
        return redireccion

    try:
        dar_de_baja_servicio(id_servicio)
    except ApiError as error:
        flash(error.mensaje, 'error')
    else:
        flash('El servicio se dio de baja correctamente.', 'success')

    return redirect(url_for('servicios_admin.listar'))


@servicios_admin_bp.route('/<int:id_servicio>/alta', methods=['POST'])
def alta(id_servicio):
    redireccion = verificar_administrador()
    if redireccion:
        return redireccion

    try:
        dar_de_alta_servicio(id_servicio)
    except ApiError as error:
        flash(error.mensaje, 'error')
    else:
        flash('El servicio se dio de alta correctamente.', 'success')

    return redirect(url_for('servicios_admin.listar'))


def _leer_cantidades_desde_formulario(servicios: list[dict]) -> list[dict]:
    items = []

    for servicio in servicios:
        try:
            cantidad = int(request.form.get(f"cantidad_{servicio['id_servicio']}", '0'))
        except ValueError:
            cantidad = 0

        if cantidad > 0:
            items.append({'id_servicio': servicio['id_servicio'], 'cantidad': cantidad})

    return items


@servicios_bp.route('/compras/<int:id_compra>/servicios', methods=['GET', 'POST'])
def paso_servicios(id_compra):
    if not verificar_autenticacion():
        flash('Debes iniciar sesión para elegir servicios.', 'warning')
        return redirigir_al_login()

    servicios = []

    try:
        servicios = listar_servicios()['servicios']

        if request.method == 'POST':
            guardar_servicios_de_compra(id_compra, _leer_cantidades_desde_formulario(servicios))
            flash('Tus servicios se guardaron correctamente.', 'success')
            return redirect(url_for('servicios.paso_servicios', id_compra=id_compra))

        elegidos = obtener_servicios_de_compra(id_compra)
    except ApiError as error:
        flash(error.mensaje, 'error')
        elegidos = {'servicios': [], 'subtotal_servicios': '0.00'}

    cantidades = {item['id_servicio']: item['cantidad'] for item in elegidos['servicios']}

    return render_template(
        'servicios.html',
        id_compra=id_compra,
        servicios=servicios,
        cantidades=cantidades,
        subtotal=elegidos['subtotal_servicios'],
    )
