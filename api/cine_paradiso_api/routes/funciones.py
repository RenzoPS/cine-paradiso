from flask import Blueprint, jsonify, request

from ..seguridad import verificar_administrador
from ..services.funciones import (
    actualizar_funcion,
    buscar_funcion,
    crear_funcion,
    eliminar_funcion,
    listar_funciones,
    listar_salas,
)

funciones_bp = Blueprint('funciones', __name__)


@funciones_bp.route('/funciones', methods=['GET'])
def obtener_funciones():
    return jsonify(listar_funciones(request.args))


@funciones_bp.route('/funciones/<id_funcion>', methods=['GET'])
def obtener_funcion(id_funcion):
    return jsonify(buscar_funcion(id_funcion))


@funciones_bp.route('/funciones', methods=['POST'])
def post_funcion():
    verificar_administrador()
    return jsonify(crear_funcion(request.get_json(silent=True))), 201


@funciones_bp.route('/funciones/<id_funcion>', methods=['PUT'])
def put_funcion(id_funcion):
    verificar_administrador()
    return jsonify(actualizar_funcion(id_funcion, request.get_json(silent=True)))


@funciones_bp.route('/funciones/<id_funcion>', methods=['DELETE'])
def delete_funcion(id_funcion):
    verificar_administrador()
    eliminar_funcion(id_funcion)
    return '', 204


@funciones_bp.route('/salas', methods=['GET'])
def obtener_salas():
    verificar_administrador()
    return jsonify(listar_salas())
