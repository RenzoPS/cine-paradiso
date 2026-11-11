from ..utils import (
    rechazar_campos_desconocidos,
    validar_cuerpo_no_vacio,
    validar_entero_positivo,
    validar_string_no_vacio,
)

def validar_id_compra(id_compra) -> int:
    return validar_entero_positivo(id_compra, 'id_compra')


def validar_cuerpo_validacion_qr(body) -> tuple[str, int]:
    datos = validar_cuerpo_no_vacio(body)
    rechazar_campos_desconocidos(datos, {'qr_token', 'id_funcion'})

    qr_token = validar_string_no_vacio(datos.get('qr_token'), 'qr_token')
    id_funcion = validar_entero_positivo(datos.get('id_funcion'), 'id_funcion')
    return qr_token, id_funcion
