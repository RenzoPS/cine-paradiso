from . import ejecutar_consulta


def listar_locales() -> list[dict]:
    return ejecutar_consulta(
        '''
        SELECT id_local, nombre AS local, direccion
        FROM locales
        ORDER BY id_local
        '''
    )
