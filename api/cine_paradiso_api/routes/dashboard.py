from flask import Blueprint, jsonify

from ..seguridad import verificar_administrador
from ..services.dashboard import obtener_dashboard


dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    verificar_administrador()
    return jsonify(obtener_dashboard())
