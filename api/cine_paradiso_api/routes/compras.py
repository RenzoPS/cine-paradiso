from flask import Blueprint, jsonify, request, send_file

from ..seguridad import verificar_administrador, verificar_autenticacion, verificar_cliente
from ..services.compras import (
    abandonar_compra,
    buscar_compra,
    cancelar_compra,
    confirmar_compra,
    crear_compra,
    listar_compras,
    listar_compras_para_validacion_admin,
    obtener_factura,
    obtener_qr_de_compra,
    validar_ingreso,
    validar_ingreso_por_id,
)

compras_bp = Blueprint('compras', __name__)


@compras_bp.route('/compras', methods=['GET'])
def get_compras():
    id_usuario = verificar_cliente()['id_usuario']
    return jsonify(listar_compras(request.args, id_usuario))


@compras_bp.route('/compras', methods=['POST'])
def post_compra():
    id_usuario = verificar_cliente()['id_usuario']
    return jsonify(crear_compra(request.get_json(silent=True), id_usuario)), 201


@compras_bp.route('/compras/admin', methods=['GET'])
def get_compras_admin():
    verificar_administrador()
    return jsonify(listar_compras_para_validacion_admin())


@compras_bp.route('/compras/<id_compra>', methods=['GET'])
def get_compra(id_compra):
    id_usuario = verificar_cliente()['id_usuario']
    return jsonify(buscar_compra(id_compra, id_usuario))


@compras_bp.route('/compras/<id_compra>', methods=['DELETE'])
def delete_compra(id_compra):
    id_usuario = verificar_cliente()['id_usuario']
    abandonar_compra(id_compra, id_usuario)
    return '', 204


@compras_bp.route('/compras/<id_compra>/confirmar', methods=['POST'])
def post_confirmar_compra(id_compra):
    id_usuario = verificar_autenticacion() ['id_usuario']
    return jsonify(confirmar_compra(id_compra, id_usuario))


@compras_bp.route('/compras/<id_compra>/cancelar', methods=['POST'])
def post_cancelar_compra(id_compra):
    id_usuario = verificar_cliente()['id_usuario']
    return jsonify(cancelar_compra(id_compra, id_usuario))


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


@compras_bp.route('/compras/<int:id_compra>/validar', methods=['POST'])
def post_validar_compra_por_id(id_compra):
    verificar_administrador()
    return jsonify(validar_ingreso_por_id(id_compra))
