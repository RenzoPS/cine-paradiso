from flask import Blueprint, jsonify

from cine_paradiso_api.services import usuarios as servicio_usuarios
from cine_paradiso_api.seguridad import verificar_autenticacion



usuarios_bp = Blueprint('usuarios', __name__)


@usuarios_bp.route('/usuarios/me', methods=['GET'])
def get_mi_perfil():
    datos_token = verificar_autenticacion()

    id_usuario = datos_token['id_usuario']

    perfil = servicio_usuarios.obtener_perfil(id_usuario)

    return jsonify(perfil), 200
