from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from cine_paradiso_web.constants import ESTADO_PENDIENTE, HORAS_LIMITE_CANCELACION, TOKEN_COOKIE_NOMBRE, TZ_ARG
from cine_paradiso_web.services.compras import abandonar_compra, cancelar_compra, confirmar_compra, obtener_compra

compras_bp = Blueprint('compras', __name__)

MENSAJE_SIN_SESION = 'Tenés que iniciar sesión para confirmar la compra'
MENSAJE_SIN_SESION_CANCELAR = 'Tenés que iniciar sesión para cancelar la compra'
MENSAJE_SIN_SESION_ABANDONAR = 'Tenés que iniciar sesión para abandonar la compra'
MENSAJE_SIN_SESION_RESUMEN = 'Tenés que iniciar sesión para ver tu compra'
MENSAJE_NO_PENDIENTE = 'Esta compra ya no está pendiente de pago'
MENSAJE_NO_DISPONIBLE = 'Todavía no disponible'


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

    vence_en = datetime.fromisoformat(compra['vence_en'])
    segundos_restantes = max(0, int((vence_en - datetime.now(TZ_ARG)).total_seconds()))

    return render_template(
        'compras/resumen.html',
        compra=compra,
        funcion=funcion,
        butacas=compra['butacas'],
        servicios=[],
        total=compra['subtotal_entradas'],
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

    return render_template(
        'compras/confirmacion.html',
        factura=factura,
        funcion=factura.get('funcion'),
        butacas=factura.get('entradas', []),
        mail_enviado=factura.get('mail_enviado'),
        compra={'id_compra': id_compra},
        horas_limite=HORAS_LIMITE_CANCELACION,
        qr_imagen=None,
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


@compras_bp.route('/compras/<int:id_compra>/abandonar', methods=['POST'])
def abandonar(id_compra):
    token = request.cookies.get(TOKEN_COOKIE_NOMBRE)

    if token is None:
        flash(MENSAJE_SIN_SESION_ABANDONAR, 'error')
        return redirect(url_for('cartelera.listar'))

    abandonada, motivo = abandonar_compra(id_compra)

    if abandonada:
        flash('Abandonaste la compra. Las butacas quedaron libres', 'success')
    else:
        flash(motivo, 'error')

    return redirect(url_for('cartelera.listar'))


# Ruta provisoria
@compras_bp.route('/compras', methods=['GET'])
def listar():
    return MENSAJE_NO_DISPONIBLE, 501