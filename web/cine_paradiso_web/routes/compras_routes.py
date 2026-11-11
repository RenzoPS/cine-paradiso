from flask import Blueprint, render_template, request

from cine_paradiso_web.constants import HORAS_LIMITE_CANCELACION, TOKEN_COOKIE_NOMBRE
from cine_paradiso_web.services.compras import confirmar_compra

compras_bp = Blueprint('compras', __name__)

MENSAJE_SIN_SESION = 'Tenés que iniciar sesión para confirmar la compra'
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
        qr_imagen=None,
    )


# Rutas provisorias: todavía no hay endpoints en la API para estas acciones.
@compras_bp.route('/compras', methods=['GET'])
def listar():
    return MENSAJE_NO_DISPONIBLE, 501


@compras_bp.route('/compras/<int:id_compra>/abandonar', methods=['POST'])
def abandonar(id_compra):
    return MENSAJE_NO_DISPONIBLE, 501


@compras_bp.route('/compras/<int:id_compra>/cancelar', methods=['GET'])
def cancelar(id_compra):
    return MENSAJE_NO_DISPONIBLE, 501