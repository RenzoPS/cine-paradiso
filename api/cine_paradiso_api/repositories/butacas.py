from . import ejecutar_consulta


def listar_butacas_de_funcion(id_funcion: int, id_sala: int) -> list[dict]:
    # Una butaca está ocupada en la función si existe su entrada.
    return ejecutar_consulta(
        '''
        SELECT b.id_butaca,
               b.fila,
               b.numero,
               EXISTS (
                   SELECT 1
                   FROM entradas e
                   WHERE e.fk_id_funcion = :id_funcion
                     AND e.fk_id_butaca = b.id_butaca
               ) AS ocupada
        FROM butacas b
        WHERE b.fk_id_sala = :id_sala
        ORDER BY b.fila, b.numero
        ''',
        {'id_funcion': id_funcion, 'id_sala': id_sala},
    )
