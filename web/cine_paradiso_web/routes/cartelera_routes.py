from flask import Blueprint, redirect, render_template, request, url_for

from cine_paradiso_web.constants import GENEROS_DISPONIBLES, SUCURSALES_DISPONIBLES
from cine_paradiso_web.services.cartelera_service import (
    obtener_pelicula_por_id,
    obtener_peliculas_cartelera,
)

cartelera_bp = Blueprint('cartelera', __name__)


@cartelera_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('cartelera.listar'))


@cartelera_bp.route('/cartelera', methods=['GET'])
def listar():
    sucursal_filtro = request.args.get('sucursal', '')
    fecha_filtro = request.args.get('fecha', 'todos')
    genero_filtro = request.args.get('genero', 'Todos')
    query_busqueda = request.args.get('q', '').strip()

    peliculas = obtener_peliculas_cartelera(
        sucursal=sucursal_filtro,
        fecha=fecha_filtro,
        genero=genero_filtro,
        busqueda=query_busqueda,
    )

    return render_template(
        'cartelera.html',
        peliculas=peliculas,
        generos=GENEROS_DISPONIBLES,
        sucursales=SUCURSALES_DISPONIBLES,
        filtro_sucursal=sucursal_filtro,
        filtro_fecha=fecha_filtro,
        filtro_genero=genero_filtro,
        query_busqueda=query_busqueda,
    )


@cartelera_bp.route('/pelicula/<int:id_pelicula>', methods=['GET'])
def detalle(id_pelicula: int):
    pelicula = obtener_pelicula_por_id(id_pelicula)

    if pelicula is None:
        # Template de detalle con estado no disponible o 404
        return render_template('detalle.html', pelicula=None, id_pelicula=id_pelicula)

    return render_template('detalle.html', pelicula=pelicula)