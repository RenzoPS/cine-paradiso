from ..utils import validar_entero_positivo

def validar_id_compra(id_compra) -> int:
    return validar_entero_positivo(id_compra, 'id_compra')