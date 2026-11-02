from flask import Blueprint, jsonify, request

from ..constants import BASE_URL
from ..services import servicios as servicios_service

# TODO (Luis): proteger con el decorador de auth: GET para cliente y admin,
# el resto solo admin.
servicios_bp = Blueprint('servicios', __name__, url_prefix=f'{BASE_URL}/servicios')


@servicios_bp.get('')
def listar_servicios():
    return jsonify(servicios_service.listar(request.args)), 200


@servicios_bp.get('/<int:servicio_id>')
def obtener_servicio(servicio_id: int):
    return jsonify(servicios_service.obtener(servicio_id)), 200


@servicios_bp.post('')
def crear_servicio():
    return jsonify(servicios_service.crear(request.get_json(silent=True))), 201


@servicios_bp.put('/<int:servicio_id>')
def modificar_servicio(servicio_id: int):
    return jsonify(servicios_service.modificar(servicio_id, request.get_json(silent=True))), 200


@servicios_bp.patch('/<int:servicio_id>')
def cambiar_estado_servicio(servicio_id: int):
    return jsonify(servicios_service.cambiar_estado(servicio_id, request.get_json(silent=True))), 200


@servicios_bp.delete('/<int:servicio_id>')
def dar_de_baja_servicio(servicio_id: int):
    servicios_service.dar_de_baja(servicio_id)

    return '', 204
