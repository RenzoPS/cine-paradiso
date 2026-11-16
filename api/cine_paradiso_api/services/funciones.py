from datetime import timedelta

from ..constants import BASE_URL
from ..paginacion import paginar
from ..repositories import transaccion
from ..repositories import funciones as db_funciones
from ..utils import ErrorAPI, formatear_fecha_hora
from ..validators.funciones import (
    validar_cuerpo_funcion,
    validar_id_funcion,
    validar_parametros_listado_funciones,
)


def _formatear_funcion(funcion: dict) -> dict:
    funcion['fecha_hora'] = formatear_fecha_hora(funcion['fecha_hora'])
    funcion['precio'] = str(funcion['precio'])
    return funcion


def listar_funciones(args) -> dict:
    limit, offset, filtros = validar_parametros_listado_funciones(args)
    funciones, total = db_funciones.listar_funciones(limit, offset, filtros)
    funciones = [_formatear_funcion(funcion) for funcion in funciones]

    return paginar(
        items=funciones,
        total=total,
        limit=limit,
        offset=offset,
        recurso='funciones',
        path=f'{BASE_URL}/funciones',
        filtros=filtros,
    )


def buscar_funcion(id_funcion) -> dict:
    id_validado = validar_id_funcion(id_funcion)
    funcion = db_funciones.obtener_funcion_por_id(id_validado)

    if funcion is None:
        raise _error_funcion_no_encontrada(id_validado)

    return _formatear_funcion(funcion)


def listar_salas() -> dict:
    return {'salas': db_funciones.listar_salas()}


def _validar_sala(conexion, id_sala: int) -> None:
    if db_funciones.bloquear_sala(conexion, id_sala) is None:
        raise ErrorAPI(
            code='sala.not.found',
            message='Sala no encontrada',
            description='No existe la sala indicada para la funcion',
            status=404,
        )


def _validar_programacion(
    conexion,
    datos: dict,
    id_funcion: int | None = None,
) -> None:
    pelicula = db_funciones.obtener_pelicula_para_funcion(conexion, datos['id_pelicula'])
    if pelicula is None:
        raise ErrorAPI(
            code='pelicula.not.found',
            message='Pelicula no encontrada',
            description='No existe la pelicula indicada para la funcion',
            status=404,
        )
    if pelicula['duracion_min'] is None or pelicula['duracion_min'] <= 0:
        raise ErrorAPI(
            code='pelicula.runtime.invalid',
            message='Duracion de pelicula invalida',
            description='La pelicula debe tener una duracion positiva para programar una funcion',
            status=409,
        )
    if pelicula['disponible_desde'] is None or pelicula['disponible_hasta'] is None:
        raise ErrorAPI(
            code='pelicula.availability.missing',
            message='Disponibilidad de pelicula incompleta',
            description='La pelicula debe tener un periodo de disponibilidad configurado',
            status=409,
        )
    if not pelicula['disponible_desde'] <= datos['fecha_hora'] <= pelicula['disponible_hasta']:
        raise ErrorAPI(
            code='funcion.outside.availability',
            message='Funcion fuera del periodo disponible',
            description='La fecha de la funcion debe estar dentro del periodo de disponibilidad de la pelicula',
            status=409,
        )

    ahora = db_funciones.obtener_hora_actual(conexion)
    if datos['fecha_hora'] <= ahora:
        raise ErrorAPI(
            code='funcion.in.past',
            message='Fecha de funcion pasada',
            description='No se pueden programar funciones en el pasado',
            status=409,
        )

    fin_funcion = datos['fecha_hora'] + timedelta(minutes=pelicula['duracion_min'])
    superpuesta = db_funciones.obtener_funcion_superpuesta(
        conexion,
        datos['id_sala'],
        datos['fecha_hora'],
        fin_funcion,
        id_funcion,
    )
    if superpuesta is not None:
        raise ErrorAPI(
            code='funcion.schedule.conflict',
            message='Conflicto de horario',
            description='La sala ya tiene otra funcion durante ese horario',
            status=409,
        )


def crear_funcion(body) -> dict:
    datos = validar_cuerpo_funcion(body)
    with transaccion() as conexion:
        _validar_sala(conexion, datos['id_sala'])
        _validar_programacion(conexion, datos)
        id_funcion = db_funciones.insertar_funcion(conexion, datos)

    funcion = db_funciones.obtener_funcion_por_id(id_funcion)
    if funcion is None:
        raise RuntimeError(f'La funcion creada con id {id_funcion} no pudo recuperarse')

    return _formatear_funcion(funcion)


def actualizar_funcion(id_funcion, body) -> dict:
    id_validado = validar_id_funcion(id_funcion)
    datos = validar_cuerpo_funcion(body)
    with transaccion() as conexion:
        id_sala_actual = db_funciones.obtener_sala_de_funcion(conexion, id_validado)
        if id_sala_actual is None:
            raise _error_funcion_no_encontrada(id_validado)

        compra = db_funciones.obtener_compra_de_funcion(conexion, id_validado)
        if compra is not None:
            raise ErrorAPI(
                code='funcion.has.sales',
                message='La función tiene compras activas',
                description='No se puede editar una función con compras pendientes o pagadas',
                status=409,
            )

        for id_sala in sorted({id_sala_actual, datos['id_sala']}):
            _validar_sala(conexion, id_sala)
        _validar_programacion(conexion, datos, id_validado)
        db_funciones.actualizar_funcion_sql(conexion, id_validado, datos)

    funcion = db_funciones.obtener_funcion_por_id(id_validado)
    if funcion is None:
        raise _error_funcion_no_encontrada(id_validado)

    return _formatear_funcion(funcion)


def _error_funcion_no_encontrada(id_funcion: int) -> ErrorAPI:
    return ErrorAPI(
        code='funcion.not.found',
        message='Funcion no encontrada',
        description=f'No existe una funcion con id {id_funcion}',
        status=404,
    )
