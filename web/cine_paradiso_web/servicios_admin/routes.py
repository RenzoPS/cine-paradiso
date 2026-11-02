"""Pantallas del backoffice para gestionar servicios.

Depende de:
    api_client.py (Gabi): llamar_api(metodo, ruta, json=None) devuelve el JSON
        de la respuesta y lanza ApiError (con .mensaje) si el back responde
        con error o no está disponible.
    auth.py (Luis): requiere_admin, decorador que exige sesión de admin.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from api_client import ApiError, llamar_api
from auth import requiere_admin

servicios_admin_bp = Blueprint(
    "servicios_admin", __name__, url_prefix="/admin/servicios"
)

RUTA_SERVICIOS = "/cine_paradiso_api/servicios"


def _datos_desde_formulario():
    return {
        "nombre": request.form.get("nombre", "").strip(),
        "descripcion": request.form.get("descripcion", "").strip() or None,
        "precio": request.form.get("precio", "").strip(),
        "imagen_url": request.form.get("imagen_url", "").strip() or None,
        "activo": request.form.get("activo") == "on",
    }


@servicios_admin_bp.get("/")
@requiere_admin
def listar():
    try:
        servicios = llamar_api("GET", f"{RUTA_SERVICIOS}?_limit=100")["servicios"]
    except ApiError as error:
        flash(error.mensaje, "error")
        servicios = []
    return render_template("admin/servicios_lista.html", servicios=servicios)


@servicios_admin_bp.route(
    "/nuevo", methods=["GET", "POST"], defaults={"servicio_id": None}
)
@servicios_admin_bp.route("/<int:servicio_id>/editar", methods=["GET", "POST"])
@requiere_admin
def formulario(servicio_id):
    editando = servicio_id is not None
    ruta = f"{RUTA_SERVICIOS}/{servicio_id}" if editando else RUTA_SERVICIOS

    if request.method == "POST":
        datos = _datos_desde_formulario()
        try:
            llamar_api("PUT" if editando else "POST", ruta, json=datos)
        except ApiError as error:
            flash(error.mensaje, "error")
            return render_template(
                "admin/servicio_form.html", servicio=datos, editando=editando
            )
        flash("Servicio guardado", "exito")
        return redirect(url_for("servicios_admin.listar"))

    servicio = None
    if editando:
        try:
            servicio = llamar_api("GET", ruta)
        except ApiError as error:
            flash(error.mensaje, "error")
            return redirect(url_for("servicios_admin.listar"))
    return render_template(
        "admin/servicio_form.html", servicio=servicio, editando=editando
    )


@servicios_admin_bp.post("/<int:servicio_id>/baja", defaults={"activo": False})
@servicios_admin_bp.post("/<int:servicio_id>/alta", defaults={"activo": True})
@requiere_admin
def cambiar_estado(servicio_id, activo):
    try:
        llamar_api(
            "PATCH", f"{RUTA_SERVICIOS}/{servicio_id}", json={"activo": activo}
        )
        flash("Servicio dado de alta" if activo else "Servicio dado de baja", "exito")
    except ApiError as error:
        flash(error.mensaje, "error")
    return redirect(url_for("servicios_admin.listar"))
