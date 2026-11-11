from flask import Blueprint, jsonify, request, send_file

from ..seguridad import verificar_administrador, verificar_autenticacion
from ..services.compras import confirmar_compra, obtener_factura, obtener_qr_de_compra, validar_ingreso

compras_bp = Blueprint('compras', __name__)


@compras_bp.route('/compras/<id_compra>/confirmar', methods=['POST'])
def post_confirmar_compra(id_compra):
    id_usuario = verificar_autenticacion() ['id_usuario']
    return jsonify(confirmar_compra(id_compra, id_usuario))


@compras_bp.route('/compras/<id_compra>/factura', methods=['GET'])
def get_factura_compra(id_compra):
    id_usuario = verificar_autenticacion()['id_usuario']
    return jsonify(obtener_factura(id_compra, id_usuario))


@compras_bp.route('/compras/<id_compra>/qr', methods=['GET'])
def get_qr_compra(id_compra):
    id_usuario = verificar_autenticacion()['id_usuario']
    return send_file(obtener_qr_de_compra(id_compra, id_usuario), mimetype='image/png')


@compras_bp.route('/compras/validar', methods=['POST'])
def post_validar_compra():
    verificar_administrador()
    return jsonify(validar_ingreso(request.get_json(silent=True)))
