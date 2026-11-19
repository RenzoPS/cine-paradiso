from datetime import datetime
from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, url_for

from cine_paradiso_web.constants import ESTADO_PENDIENTE, HORAS_LIMITE_CANCELACION, TOKEN_COOKIE_NOMBRE
from cine_paradiso_web.services.api_service import ApiError
from cine_paradiso_web.services.compras import (
    abandonar_compra,
    cancelar_compra,
    confirmar_compra,
    listar_compras_usuario,
    obtener_compra,
    obtener_qr_base64,
    segundos_para_vencer,
)
from cine_paradiso_web.services.servicios_service import obtener_servicios_de_compra

compras_bp = Blueprint('compras', __name__)

MENSAJE_SIN_SESION = 'Tenés que iniciar sesión para confirmar la compra'
MENSAJE_SIN_SESION_CANCELAR = 'Tenés que iniciar sesión para cancelar la compra'
MENSAJE_SIN_SESION_ABANDONAR = 'Tenés que iniciar sesión para abandonar la compra'
MENSAJE_SIN_SESION_RESUMEN = 'Tenés que iniciar sesión para ver tu compra'
MENSAJE_NO_PENDIENTE = 'Esta compra ya no está pendiente de pago'
MENSAJE_SIN_SESION_ENTRADAS = 'Tenés que iniciar sesión para ver tus entradas'
MENSAJE_NO_DISPONIBLE = 'Todavía no disponible'


def _servicios_y_total(id_compra, subtotal_entradas):
    servicios = []
    subtotal_servicios = Decimal('0')

    try:
        elegidos = obtener_servicios_de_compra(id_compra)
        servicios = elegidos['servicios']
        subtotal_servicios = Decimal(str(elegidos['subtotal_servicios']))
    except ApiError as error:
        flash(error.mensaje, 'error')

    total = Decimal(str(subtotal_entradas)) + subtotal_servicios

    return servicios, f'{total:.2f}'


@compras_bp.route('/compras/<int:id_compra>/resumen', methods=['GET'])
def resumen(id_compra):
    token = request.cookies.get(TOKEN_COOKIE_NOMBRE)

    if token is None:
        flash(MENSAJE_SIN_SESION_RESUMEN, 'error')
        return redirect(url_for('cartelera.listar'))

    compra, motivo = obtener_compra(id_compra)

    if motivo is not None:
        flash(motivo, 'error')
        return redirect(url_for('cartelera.listar'))

    if compra['estado'] != ESTADO_PENDIENTE:
        flash(MENSAJE_NO_PENDIENTE, 'error')
        return redirect(url_for('cartelera.listar'))

    funcion = compra['funcion']
    funcion['fecha_hora'] = datetime.fromisoformat(funcion['fecha_hora']).strftime('%d/%m/%Y %H:%M')

    segundos_restantes = segundos_para_vencer(compra)

    servicios, total = _servicios_y_total(id_compra, compra['subtotal_entradas'])

    return render_template(
        'compras/resumen.html',
        compra=compra,
        funcion=funcion,
        butacas=compra['butacas'],
        servicios=servicios,
        total=total,
        segundos_restantes=segundos_restantes,
    )


@compras_bp.route('/compras/<int:id_compra>/confirmar', methods=['POST'])
def confirmar(id_compra):
    token = request.cookies.get(TOKEN_COOKIE_NOMBRE)

    if token is None:
        return render_template('compras/no_confirmada.html', motivo=MENSAJE_SIN_SESION)

    factura, motivo = confirmar_compra(id_compra)

    if motivo is not None:
        return render_template('compras/no_confirmada.html', motivo=motivo)

    qr_imagen = obtener_qr_base64(id_compra, token)

    return render_template(
        'compras/confirmacion.html',
        factura=factura,
        funcion=factura.get('funcion'),
        butacas=factura.get('entradas', []),
        mail_enviado=factura.get('mail_enviado'),
        compra={'id_compra': id_compra},
        horas_limite=HORAS_LIMITE_CANCELACION,
        qr_imagen=qr_imagen,
    )


@compras_bp.route('/compras', methods=['GET'])
def listar():
    token = request.cookies.get(TOKEN_COOKIE_NOMBRE)

    if token is None:
        flash(MENSAJE_SIN_SESION_ENTRADAS, 'error')
        return redirect(url_for('auth.login'))

    compras, motivo = listar_compras_usuario(token)

    if motivo is not None:
        flash(motivo, 'error')

    for compra in compras:
        if compra.get('tiene_qr'):
            compra['qr_imagen'] = obtener_qr_base64(compra['id_compra'], token)
        else:
            compra['qr_imagen'] = None

    return render_template(
        'compras/mis_entradas.html',
        compras=compras,
        horas_limite=HORAS_LIMITE_CANCELACION,
    )

@compras_bp.route('/compras/<int:id_compra>/cancelar', methods=['GET'])
def cancelar(id_compra):
    return render_template(
        'compras/cancelar.html',
        id_compra=id_compra,
        horas_limite=HORAS_LIMITE_CANCELACION,
    )


@compras_bp.route('/compras/<int:id_compra>/cancelar', methods=['POST'])
def confirmar_cancelacion(id_compra):
    token = request.cookies.get(TOKEN_COOKIE_NOMBRE)

    if token is None:
        return render_template('compras/cancelada.html', motivo=MENSAJE_SIN_SESION_CANCELAR)

    _, motivo = cancelar_compra(id_compra)

    return render_template('compras/cancelada.html', motivo=motivo)


def _id_funcion_de(compra):
    id_funcion = None

    if compra is not None:
        id_funcion = compra.get('id_funcion') or (compra.get('funcion') or {}).get('id_funcion')

    return id_funcion


@compras_bp.route('/compras/<int:id_compra>/abandonar', methods=['POST'])
def abandonar(id_compra):
    token = request.cookies.get(TOKEN_COOKIE_NOMBRE)

    if token is None:
        flash(MENSAJE_SIN_SESION_ABANDONAR, 'error')
        return redirect(url_for('cartelera.listar'))

    compra, _ = obtener_compra(id_compra)
    id_funcion = _id_funcion_de(compra)

    abandonada, motivo = abandonar_compra(id_compra)

    if abandonada:
        flash('Abandonaste la compra. Las butacas quedaron libres', 'success')
    else:
        flash(motivo, 'error')

    destino = url_for('butacas.butacas', id_funcion=id_funcion) if id_funcion else url_for('cartelera.listar')
    return redirect(destino)
