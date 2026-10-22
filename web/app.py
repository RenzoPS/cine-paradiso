import logging

from flask import Flask

from cine_paradiso_web.constants import SECRET_KEY, WEB_PORT

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = SECRET_KEY

# app.register_blueprint(<recurso>_bp)


if __name__ == '__main__':
    app.run(debug=True, port=WEB_PORT)
