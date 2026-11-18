from flask import Blueprint, jsonify

from ..services.locales import listar_locales


locales_bp = Blueprint('locales', __name__)


@locales_bp.route('/locales', methods=['GET'])
def obtener_locales():
    return jsonify(listar_locales())
