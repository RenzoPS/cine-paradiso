import logging
from datetime import datetime

from flask import Flask

from cine_paradiso_web.constants import SECRET_KEY, WEB_PORT
from cine_paradiso_web.routes.admin_routes import admin_bp
from cine_paradiso_web.routes.cartelera_routes import cartelera_bp
from cine_paradiso_web.routes.compras_routes import compras_bp
from cine_paradiso_web.routes.butacas_routes import butacas_bp
from cine_paradiso_web.routes.servicios_routes import servicios_admin_bp, servicios_bp
from cine_paradiso_web.routes.auth import auth_bp
from cine_paradiso_web.routes.usuarios import usuarios_bp
from cine_paradiso_web.services.api_service import ApiError
from cine_paradiso_web.services.locales_service import listar_locales

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = SECRET_KEY


@app.template_filter('fecha_legible')
def _filtro_fecha_legible(valor):
    if not valor:
        return ''
    fecha = datetime.fromisoformat(str(valor))
    return fecha.strftime('%d/%m/%Y %H:%M')

@app.context_processor
def cargar_locales():
    try:
        return {'locales': listar_locales()['locales']}
    except ApiError:
        logging.exception('No se pudieron cargar los locales.')
        return {'locales': []}

app.register_blueprint(cartelera_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(compras_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(usuarios_bp)

app.register_blueprint(butacas_bp)
app.register_blueprint(servicios_admin_bp)
app.register_blueprint(servicios_bp)

if __name__ == '__main__':
    app.run(debug=True, port=WEB_PORT)
