from flask import Blueprint, jsonify, request, make_response

from cine_paradiso_api.services import auth as servicio_auth
from cine_paradiso_api.validators import auth as validador_auth
from cine_paradiso_api.constants import (
    TOKEN_COOKIE_NOMBRE,
    TOKEN_DURACION_SEGUNDOS,
)
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/auth/registro', methods=['POST'])
def post_registro():
    datos = validador_auth.validar_registro(request.get_json(silent=True))
    return jsonify(servicio_auth.registrar_usuario(datos)), 201


@auth_bp.route('/auth/login', methods=['POST'])
def post_login():
    datos = validador_auth.validar_login(request.get_json(silent=True))

    resultado = servicio_auth.iniciar_sesion(datos)

    respuesta = make_response(jsonify(resultado), 200)

    respuesta.set_cookie(
        TOKEN_COOKIE_NOMBRE,
        resultado['token'],
        max_age=TOKEN_DURACION_SEGUNDOS,
        httponly=True,
        samesite='Lax',
        secure=False,
    )

    return respuesta
