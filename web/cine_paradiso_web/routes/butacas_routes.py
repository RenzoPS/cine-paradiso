from flask import Blueprint, flash, redirect, render_template, request, url_for

from cine_paradiso_web.constants import TOKEN_COOKIE_NOMBRE
from cine_paradiso_web.services.api_service import ApiError
from cine_paradiso_web.services.butacas_services import (
    crear_compra_butacas,
    obtener_mapa_butacas,
)

butacas_bp = Blueprint('butacas', __name__)


@butacas_bp.route('/funciones/<int:id_funcion>/butacas', methods=['GET', 'POST'])
def butacas(id_funcion: int):
    if request.method == 'POST':
        if not request.cookies.get(TOKEN_COOKIE_NOMBRE):
            flash('Tenés que iniciar sesión para reservar butacas.', 'error')
            return redirect(url_for('auth.login'))

        butacas_seleccionadas = request.form.getlist('butacas')
        if not butacas_seleccionadas:
            flash('Seleccioná al menos una butaca para continuar.', 'warning')
            return redirect(url_for('butacas.butacas', id_funcion=id_funcion))

        try:
            ids_butacas = [int(id_b) for id_b in butacas_seleccionadas]
            compra = crear_compra_butacas(id_funcion, ids_butacas)
            return redirect(url_for('compras.resumen', id_compra=compra['id_compra']))
        except ApiError as error:
            flash(error.mensaje, 'error')
            return redirect(url_for('butacas.butacas', id_funcion=id_funcion))

    try:
        mapa = obtener_mapa_butacas(id_funcion)
    except ApiError as error:
        flash(error.mensaje, 'error')
        mapa = {'funcion': {}, 'capacidad': 0, 'disponibles': 0, 'filas': []}

    return render_template(
        'butacas.html',
        id_funcion=id_funcion,
        funcion=mapa.get('funcion', {}),
        filas=mapa.get('filas', []),
        capacidad=mapa.get('capacidad', 0),
        disponibles=mapa.get('disponibles', 0),
    )

