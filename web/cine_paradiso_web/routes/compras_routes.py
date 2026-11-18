from flask import Blueprint, flash, redirect, render_template, request, url_for

from cine_paradiso_web.constants import HORAS_LIMITE_CANCELACION, TOKEN_COOKIE_NOMBRE
from cine_paradiso_web.services.compras import (
    confirmar_compra,
    listar_compras_usuario,
    obtener_qr_base64,
)

compras_bp = Blueprint('compras', __name__)

MENSAJE_SIN_SESION = 'Tenés que iniciar sesión para confirmar la compra'
MENSAJE_SIN_SESION_ENTRADAS = 'Tenés que iniciar sesión para ver tus entradas'
MENSAJE_NO_DISPONIBLE = 'Todavía no disponible'


@compras_bp.route('/compras/<int:id_compra>/confirmar', methods=['POST'])
def confirmar(id_compra):
    token = request.cookies.get(TOKEN_COOKIE_NOMBRE)

    if token is None:
        return render_template('compras/no_confirmada.html', motivo=MENSAJE_SIN_SESION)

    factura, motivo = confirmar_compra(id_compra, token)

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
        qr_imagen=obtener_qr_base64(id_compra, token),
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


# Rutas provisorias: todavía no hay endpoints en la API para estas acciones.
@compras_bp.route('/compras/<int:id_compra>/abandonar', methods=['POST'])
def abandonar(id_compra):
    return MENSAJE_NO_DISPONIBLE, 501


@compras_bp.route('/compras/<int:id_compra>/cancelar', methods=['GET'])
def cancelar(id_compra):
    return MENSAJE_NO_DISPONIBLE, 501