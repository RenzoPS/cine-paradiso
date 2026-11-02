from flask import Blueprint, jsonify, request, send_file

from ..seguridad import admin_required, login_required, obtener_datos_token
from ..services.compras import confirmar_compra, obtener_factura, obtener_qr_de_compra, validar_ingreso

compras_bp = Blueprint('compras', __name__)


@compras_bp.route('/compras/<id_compra>/confirmar', methods=['POST'])
@login_required
def post_confirmar_compra(id_compra):
    id_usuario = obtener_datos_token()['id_usuario']
    return jsonify(confirmar_compra(id_compra, id_usuario))


@compras_bp.route('/compras/<id_compra>/factura', methods=['GET'])
@login_required
def get_factura_compra(id_compra):
    id_usuario = obtener_datos_token()['id_usuario']
    return jsonify(obtener_factura(id_compra, id_usuario))


@compras_bp.route('/compras/<id_compra>/qr', methods=['GET'])
@login_required
def get_qr_compra(id_compra):
    id_usuario = obtener_datos_token()['id_usuario']
    return send_file(obtener_qr_de_compra(id_compra, id_usuario), mimetype='image/png')


@compras_bp.route('/compras/validar', methods=['POST'])
@admin_required
def post_validar_compra():
    return jsonify(validar_ingreso(request.get_json(silent=True)))
