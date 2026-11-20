from flask import Blueprint, jsonify

from ..services.butacas import obtener_mapa_butacas

butacas_bp = Blueprint('butacas', __name__)


@butacas_bp.route('/funciones/<id_funcion>/butacas', methods=['GET'])
def obtener_butacas_funcion(id_funcion):
    return jsonify(obtener_mapa_butacas(id_funcion))
