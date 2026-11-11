from flask import Blueprint, redirect, render_template, request, url_for

butacas_bp = Blueprint('butacas', __name__)


@butacas_bp.route('/butacas', methods=['GET', 'POST'])
def butacas():
    if request.method == 'POST':
        butacas_seleccionadas = request.form.getlist('butacas')
        print("Butacas seleccionadas:", butacas_seleccionadas)
        return redirect(url_for('butacas.butacas'))


    lista_peliculas = [
        {"titulo": "Inception", "fecha_hora": "2026-11-10 18:00", "sala": "Sala 1 (IMAX)"},
        {"titulo": "Interstellar", "fecha_hora": "2026-11-10 21:00", "sala": "Sala 3"},
        {"titulo": "The Matrix", "fecha_hora": "2026-11-11 16:30", "sala": "Sala 2 (3D)"}
    ]
    return render_template("butacas.html", pelicula=lista_peliculas)
