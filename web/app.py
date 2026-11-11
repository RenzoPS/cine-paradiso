import logging

from flask import Flask

from cine_paradiso_web.constants import SECRET_KEY, WEB_PORT
from cine_paradiso_web.routes.admin_routes import admin_bp
from cine_paradiso_web.routes.cartelera_routes import cartelera_bp
from cine_paradiso_web.routes.auth import auth_bp
from cine_paradiso_web.routes.usuarios import usuarios_bp

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = SECRET_KEY

app.register_blueprint(cartelera_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(usuarios_bp)


if __name__ == '__main__':
    app.run(debug=True, port=WEB_PORT)
