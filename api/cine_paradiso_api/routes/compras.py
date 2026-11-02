from flask import Blueprint, jsonify

from ..seguridad import login_required, obtener_datos_token
from ..services.compras import confirmar_compra, obtener_factura

compras_bp = Blueprint('compras', __name__)


@compras_bp.route('/compras/<id_compra>/confirmar', methods=['POST'])
@login_required
def post_confirmar_compra(id_compra):
    id_usuario = obtener_datos_token()['id_usuario']
    return jsonify(confirmar_compra(id_compra, id_usuario))


@compras_bp.route('/compras/<id_compra>/factura', methods=['GET'])
@login_required
def get_factura_compra(id_compra):
    id_usuario = obtener_datos_token()['id_usuario']
    return jsonify(obtener_factura(id_compra, id_usuario))
