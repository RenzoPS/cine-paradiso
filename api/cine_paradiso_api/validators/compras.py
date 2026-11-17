from ..constants import ERROR_CODE_INVALID_FORMAT, MAX_BUTACAS_POR_COMPRA
from ..utils import (
    ErrorAPI,
    rechazar_campos_desconocidos,
    validar_cuerpo_no_vacio,
    validar_entero_positivo,
    validar_maximo,
    validar_minimo,
    validar_string_no_vacio,
)

CAMPOS_COMPRA = {'id_funcion', 'butacas'}


def validar_id_compra(id_compra) -> int:
    return validar_entero_positivo(id_compra, 'id_compra')


def validar_cuerpo_validacion_qr(body) -> tuple[str, int]:
    datos = validar_cuerpo_no_vacio(body)
    rechazar_campos_desconocidos(datos, {'qr_token', 'id_funcion'})

    qr_token = validar_string_no_vacio(datos.get('qr_token'), 'qr_token')
    id_funcion = validar_entero_positivo(datos.get('id_funcion'), 'id_funcion')
    return qr_token, id_funcion


def validar_cuerpo_compra(body) -> tuple[int, list[int]]:
    datos = validar_cuerpo_no_vacio(body)
    rechazar_campos_desconocidos(datos, CAMPOS_COMPRA)

    for campo in sorted(CAMPOS_COMPRA):
        if campo not in datos:
            raise ErrorAPI(
                code=f'required.{campo}',
                message=f"Campo requerido: '{campo}'",
                description=f"El campo '{campo}' es obligatorio"
            )

    id_funcion = validar_entero_positivo(datos['id_funcion'], 'id_funcion')

    if not isinstance(datos['butacas'], list):
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_FORMAT,
            message="Formato de 'butacas' invalido",
            description="El campo 'butacas' debe ser una lista de identificadores de butaca"
        )

    validar_minimo(len(datos['butacas']), 1, 'butacas')
    validar_maximo(len(datos['butacas']), MAX_BUTACAS_POR_COMPRA, 'butacas')
    butacas = [validar_entero_positivo(id_butaca, 'butacas') for id_butaca in datos['butacas']]

    if len(set(butacas)) != len(butacas):
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_FORMAT,
            message="Formato de 'butacas' invalido",
            description="El campo 'butacas' no puede repetir una butaca"
        )

    return id_funcion, butacas
