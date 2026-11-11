from flask import Blueprint, abort, redirect, render_template, request, url_for

from cine_paradiso_web.constants import GENEROS_DISPONIBLES, PELICULAS, SUCURSALES_DISPONIBLES

butacas_bp = Blueprint('butacas', __name__)


@butacas_bp.route('/butacas', methods=['GET', 'POST'])
def butacas():
    lista_peliculas = [
        {"titulo": "Inception", "fecha_hora": "2026-11-10 18:00", "sala": "Sala 1 (IMAX)"},
        {"titulo": "Interstellar", "fecha_hora": "2026-11-10 21:00", "sala": "Sala 3"},
        {"titulo": "The Matrix", "fecha_hora": "2026-11-11 16:30", "sala": "Sala 2 (3D)"}
    ]
    return render_template("butacas.html", pelicula = lista_peliculas)

@butacas_bp.route('/butaca', methods=['GET'])
def listar_butacas():
    sucursal_filtro = request.args.get('sucursal', '')
    fecha_filtro = request.args.get('fecha', 'todos')
    genero_filtro = request.args.get('genero', 'Todos')
    query_busqueda = request.args.get('q', '').strip()
    peliculas = PELICULAS

    return render_template(
        'cartelera.html',
        peliculas=peliculas,
        generos=GENEROS_DISPONIBLES,
        sucursales=SUCURSALES_DISPONIBLES,
        filtro_sucursal=sucursal_filtro,
        filtro_fecha=fecha_filtro,
        filtro_genero=genero_filtro,
        query_busqueda=query_busqueda
    )


@butacas_bp.route('/pelicula/<int:id_pelicula>', methods=['GET'])
def detalle(id_pelicula: int):
    pelicula = next((p for p in PELICULAS if p.get('id') == id_pelicula), None)

    if pelicula is None:
        # Template de detalle con estado no disponible o 404
        return render_template('detalle.html', pelicula=None, id_pelicula=id_pelicula)

    return render_template('detalle.html', pelicula=pelicula)
