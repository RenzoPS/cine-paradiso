from flask import Blueprint, abort, redirect, render_template, request, url_for

cartelera_bp = Blueprint('cartelera', __name__)

# Estructura lista para conectarse con la API / Base de Datos
PELICULAS = []

GENEROS_DISPONIBLES = [
    'Todos', 'Drama', 'Comedia', 'Acción', 'Ciencia Ficción', 'Suspenso', 'Terror', 'Aventura', 'Romance'
]

SUCURSALES_DISPONIBLES = [
    {'id': '', 'nombre': 'Todas las sedes'},
    {'id': '1', 'nombre': 'Sucursal Centro'},
    {'id': '2', 'nombre': 'Sucursal Belgrano'},
    {'id': '3', 'nombre': 'Sucursal Recoleta'}
]


@cartelera_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('cartelera.listar'))


@cartelera_bp.route('/cartelera', methods=['GET'])
def listar():
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


@cartelera_bp.route('/pelicula/<int:id_pelicula>', methods=['GET'])
def detalle(id_pelicula: int):
    pelicula = next((p for p in PELICULAS if p.get('id') == id_pelicula), None)

    if pelicula is None:
        # Template de detalle con estado no disponible o 404
        return render_template('detalle.html', pelicula=None, id_pelicula=id_pelicula)

    return render_template('detalle.html', pelicula=pelicula)
