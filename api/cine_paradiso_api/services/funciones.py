from datetime import timedelta

from ..constants import BASE_URL, ESTADO_PAGADA, MINUTOS_APERTURA_SALA, MINUTOS_LIMPIEZA_SALA
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

    # Entre funciones de una misma sala tiene que quedar el margen de limpieza y apertura.
    margen_minutos = MINUTOS_LIMPIEZA_SALA + MINUTOS_APERTURA_SALA
    margen = timedelta(minutes=margen_minutos)
    fin_funcion = datos['fecha_hora'] + timedelta(minutes=pelicula['duracion_min'])
    superpuesta = db_funciones.obtener_funcion_superpuesta(
        conexion,
        datos['id_sala'],
        datos['fecha_hora'] - margen,
        fin_funcion + margen,
        id_funcion,
    )
    if superpuesta is not None:
        raise ErrorAPI(
            code='funcion.schedule.conflict',
            message='Conflicto de horario',
            description=f'La sala ya tiene otra funcion en ese horario o a menos de {margen_minutos} minutos',
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

        # Verificar que la función no esté cancelada
        funcion_actual = db_funciones.obtener_funcion_por_id(id_validado)
        if funcion_actual and funcion_actual.get('cancelada'):
            raise ErrorAPI(
                code='funcion.cancelada',
                message='Función cancelada',
                description='No se puede editar una función que fue cancelada',
                status=409,
            )

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


def cancelar_funcion(id_funcion) -> dict:
    """
    El administrador cancela una función completa: marca la función como cancelada,
    cancela todas sus compras pagadas y pendientes, libera las butacas y envía
    mail a cada cliente afectado. Todo en una sola transacción.
    """
    # Import interno para evitar import circular con services/compras.py
    from .compras import (
        vencer_reservas_de_funcion,
        ESTADOS_CANCELABLES_POR_ADMIN,
        ESTADO_PAGADA,
        CANCELADA_POR_ADMIN,
        _enviar_mail_cancelacion_admin,
    )
    from ..repositories import transaccion
    from ..repositories import funciones as db_funciones
    from ..repositories import compras as db_compras

    id_validado = validar_id_funcion(id_funcion)

    # 1. Vencer reservas viejas (lazy) para tener estados reales
    vencer_reservas_de_funcion(id_validado)

    # 2. Obtener compras cancelables (pagadas + pendientes) y validaciones
    with transaccion() as conexion:
        # Bloquear la función para evitar race conditions
        db_compras.bloquear_funcion(conexion, id_validado)
        
        # Verificar que la función existe
        funcion = db_funciones.obtener_funcion_por_id(id_validado)
        if funcion is None:
            raise ErrorAPI(
                code='funcion.not.found',
                message='Función no encontrada',
                description=f'No existe una función con id {id_validado}',
                status=404,
            )
        
        # Verificar que no esté ya cancelada
        if funcion.get('cancelada'):
            raise ErrorAPI(
                code='funcion.ya.cancelada',
                message='Función ya cancelada',
                description='La función ya fue cancelada anteriormente',
                status=409,
            )
        
        # Verificar que no haya empezado
        from datetime import datetime
        ahora = datetime.now()
        # Convertir fecha_hora a datetime si es string
        fecha_funcion = funcion['fecha_hora']
        if isinstance(fecha_funcion, str):
            fecha_funcion = datetime.fromisoformat(fecha_funcion.replace('Z', '+00:00'))
        if fecha_funcion <= ahora:
            raise ErrorAPI(
                code='funcion.ya.comenzo',
                message='La función ya comenzó',
                description='No se puede cancelar una función que ya empezó',
                status=409,
            )
        
        # Obtener compras cancelables con FOR UPDATE
        compras = db_funciones.compras_cancelables(conexion, id_validado)

        # 3. Leer datos para mail ANTES de borrar entradas
        para_mail = []
        for compra in compras:
            para_mail.append((
                compra['id_compra'],
                db_compras.obtener_datos_para_mail(compra['id_compra']),
                db_compras.obtener_entradas_de_compra(compra['id_compra']),
                compra['estado'] == ESTADO_PAGADA,  # tenia_qr
            ))

        # 4. Marcar función cancelada + cancelar cada compra + liberar butacas
        db_funciones.marcar_funcion_cancelada(conexion, id_validado)
        for compra in compras:
            db_compras.marcar_compra_cancelada(conexion, compra['id_compra'], CANCELADA_POR_ADMIN)
            db_compras.eliminar_entradas_de_compra(conexion, compra['id_compra'])

    # 5. Enviar mails (fuera de la transacción)
    mails_enviados = 0
    for id_compra, datos, entradas, tenia_qr in para_mail:
        if _enviar_mail_cancelacion_admin(id_compra, datos, entradas, tenia_qr):
            mails_enviados += 1

    return {
        'id_funcion': id_validado,
        'cancelada': True,
        'compras_canceladas': len(compras),
        'mails_enviados': mails_enviados,
    }


def preview_cancelar_funcion(id_funcion) -> dict:
    """
    Preview de cancelación: cuenta cuántas compras se cancelarían sin ejecutar la cancelación.
    """
    from .compras import (
        vencer_reservas_de_funcion,
    )
    from ..repositories import transaccion
    from ..repositories import funciones as db_funciones
    from ..repositories import compras as db_compras

    id_validado = validar_id_funcion(id_funcion)

    # 1. Vencer reservas viejas (lazy)
    vencer_reservas_de_funcion(id_validado)

    # 2. Obtener compras cancelables
    with transaccion() as conexion:
        db_compras.bloquear_funcion(conexion, id_validado)
        
        funcion = db_funciones.obtener_funcion_por_id(id_validado)
        if funcion is None:
            raise ErrorAPI(
                code='funcion.not.found',
                message='Función no encontrada',
                description=f'No existe una función con id {id_validado}',
                status=404,
            )
        
        if funcion.get('cancelada'):
            raise ErrorAPI(
                code='funcion.ya.cancelada',
                message='Función ya cancelada',
                description='La función ya fue cancelada anteriormente',
                status=409,
            )
        
        from datetime import datetime
        ahora = datetime.now()
        fecha_funcion = funcion['fecha_hora']
        if isinstance(fecha_funcion, str):
            fecha_funcion = datetime.fromisoformat(fecha_funcion.replace('Z', '+00:00'))
        if fecha_funcion <= ahora:
            raise ErrorAPI(
                code='funcion.ya.comenzo',
                message='La función ya comenzó',
                description='No se puede cancelar una función que ya empezó',
                status=409,
            )
        
        compras = db_funciones.compras_cancelables(conexion, id_validado)

    return {
        'id_funcion': id_validado,
        'compras_a_cancelar': len(compras),
        'detalle': [
            {'id_compra': c['id_compra'], 'estado': c['estado']}
            for c in compras
        ],
    }
