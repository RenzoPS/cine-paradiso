from flask import Blueprint, jsonify, request

from ..seguridad import verificar_administrador, verificar_cliente
from ..services.servicios import (
    actualizar_servicio,
    buscar_servicio,
    buscar_servicios_de_compra,
    crear_servicio,
    definir_servicios_de_compra,
    eliminar_servicio,
    listar_servicios,
)

servicios_bp = Blueprint('servicios', __name__)


@servicios_bp.route('/servicios', methods=['GET'])
def get_servicios():
    return jsonify(listar_servicios(request.args))


@servicios_bp.route('/servicios/<id_servicio>', methods=['GET'])
def get_servicio(id_servicio):
    return jsonify(buscar_servicio(id_servicio))


@servicios_bp.route('/servicios', methods=['POST'])
def post_servicio():
    verificar_administrador()
    return jsonify(crear_servicio(request.get_json(silent=True))), 201


@servicios_bp.route('/servicios/<id_servicio>', methods=['PUT'])
def put_servicio(id_servicio):
    verificar_administrador()
    return jsonify(actualizar_servicio(id_servicio, request.get_json(silent=True)))


@servicios_bp.route('/servicios/<id_servicio>', methods=['DELETE'])
def delete_servicio(id_servicio):
    verificar_administrador()
    return jsonify(eliminar_servicio(id_servicio))


@servicios_bp.route('/compras/<id_compra>/servicios', methods=['GET'])
def get_servicios_de_compra(id_compra):
    id_usuario = verificar_cliente()['id_usuario']
    return jsonify(buscar_servicios_de_compra(id_compra, id_usuario))


@servicios_bp.route('/compras/<id_compra>/servicios', methods=['PUT'])
def put_servicios_de_compra(id_compra):
    id_usuario = verificar_cliente()['id_usuario']
    return jsonify(definir_servicios_de_compra(id_compra, request.get_json(silent=True), id_usuario))
