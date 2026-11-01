from flask import Blueprint, jsonify, request

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
def get_peliculas():
    return jsonify(listar_peliculas(request.args))


@peliculas_bp.route('/peliculas', methods=['POST'])
def post_pelicula():
    pelicula = importar_pelicula(request.get_json(silent=True))
    return jsonify(pelicula), 201


@peliculas_bp.route('/peliculas/tmdb', methods=['GET'])
def get_peliculas_tmdb():
    return jsonify(buscar_peliculas_tmdb(request.args))


@peliculas_bp.route('/peliculas/<id_pelicula>', methods=['GET'])
def get_pelicula(id_pelicula):
    return jsonify(buscar_pelicula(id_pelicula))


@peliculas_bp.route('/peliculas/<id_pelicula>', methods=['PUT'])
def put_pelicula(id_pelicula):
    pelicula = actualizar_pelicula(id_pelicula, request.get_json(silent=True))
    return jsonify(pelicula)


@peliculas_bp.route('/peliculas/<id_pelicula>', methods=['DELETE'])
def delete_pelicula(id_pelicula):
    return jsonify(eliminar_pelicula(id_pelicula))
