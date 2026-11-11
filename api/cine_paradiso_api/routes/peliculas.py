from flask import Blueprint, jsonify, request

from ..seguridad import admin_required
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
@admin_required
def obtener_peliculas_tmdb():
    return jsonify(buscar_peliculas_tmdb(request.args))


@peliculas_bp.route('/peliculas', methods=['POST'])
@admin_required
def crear_pelicula():
    pelicula = importar_pelicula(request.get_json(silent=True))
    return jsonify(pelicula), 201


@peliculas_bp.route('/peliculas/<id_pelicula>', methods=['PUT'])
@admin_required
def reemplazar_pelicula(id_pelicula):
    return jsonify(actualizar_pelicula(id_pelicula, request.get_json(silent=True)))


@peliculas_bp.route('/peliculas/<id_pelicula>', methods=['DELETE'])
@admin_required
def dar_de_baja_pelicula(id_pelicula):
    return jsonify(eliminar_pelicula(id_pelicula))
