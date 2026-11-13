from cine_paradiso_api.constants import ERROR_CODE_USUARIO_NO_ENCONTRADO
from cine_paradiso_api.repositories import usuarios as repositorio_usuarios
from cine_paradiso_api.utils import ErrorAPI, formatear_fecha_hora


def obtener_perfil(id_usuario):
    usuario = repositorio_usuarios.obtener_usuario_por_id(id_usuario)

    if not usuario:
        raise ErrorAPI(
            code=ERROR_CODE_USUARIO_NO_ENCONTRADO,
            message='Usuario no encontrado',
            description=f"No existe un usuario con id '{id_usuario}'",
            status=404
        )

    return {
        'id_usuario': usuario['id_usuario'],
        'nombre': usuario['nombre'],
        'apellido': usuario['apellido'],
        'email': usuario['email'],
        'rol': usuario['rol'],
        'fecha_creacion': formatear_fecha_hora(usuario['fecha_creacion']),
    }



