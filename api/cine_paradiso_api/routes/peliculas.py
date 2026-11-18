from flask import Blueprint, jsonify, request

from ..seguridad import verificar_administrador
from ..services.peliculas import (
    actualizar_pelicula,
    buscar_pelicula,
    buscar_peliculas_tmdb,
    eliminar_pelicula,
    importar_pelicula,
    listar_peliculas,
)

peliculas_bp = Blueprint('peliculas', __name__)


@peliculas_bp.route('/peliculas', methods=['GET'])
def obtener_peliculas():
    return jsonify(listar_peliculas(request.args))


@peliculas_bp.route('/peliculas/<id_pelicula>', methods=['GET'])
def obtener_pelicula(id_pelicula):
    return jsonify(buscar_pelicula(id_pelicula))


@peliculas_bp.route('/peliculas/tmdb', methods=['GET'])
def obtener_peliculas_tmdb():
    verificar_administrador()
    return jsonify(buscar_peliculas_tmdb(request.args))


@peliculas_bp.route('/peliculas', methods=['POST'])
def crear_pelicula():
    verificar_administrador()
    pelicula = importar_pelicula(request.get_json(silent=True))
    return jsonify(pelicula), 201


@peliculas_bp.route('/peliculas/<id_pelicula>', methods=['PUT'])
def reemplazar_pelicula(id_pelicula):
    verificar_administrador()
    return jsonify(actualizar_pelicula(id_pelicula, request.get_json(silent=True)))


@peliculas_bp.route('/peliculas/<id_pelicula>', methods=['DELETE'])
def dar_de_baja_pelicula(id_pelicula):
    verificar_administrador()
    return jsonify(eliminar_pelicula(id_pelicula))
