import logging

from flask import Flask, jsonify

from cine_paradiso_api import repositories
from cine_paradiso_api.constants import API_PORT, BASE_URL
from cine_paradiso_api.utils import ErrorAPI, construir_error_api

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')

app = Flask(__name__)
app.json.sort_keys = False

repositories.init_app(app)

# app.register_blueprint(<recurso>_bp, url_prefix=BASE_URL)


@app.errorhandler(ErrorAPI)
def manejar_error_api(e: ErrorAPI):
    return jsonify(e.payload), e.status


@app.errorhandler(404)
def manejar_no_encontrado(e):
    return jsonify(construir_error_api(
        code='not.found',
        message='Recurso no encontrado',
        description='La ruta solicitada no existe'
    )), 404


@app.errorhandler(405)
def manejar_metodo_no_permitido(e):
    return jsonify(construir_error_api(
        code='method.not.allowed',
        message='Metodo no permitido',
        description='El metodo HTTP no esta soportado para esta ruta'
    )), 405


@app.errorhandler(Exception)
def manejar_error_inesperado(e):
    if app.debug:
        raise e

    logging.exception('Error inesperado')

    return jsonify(construir_error_api(
        code='internal.error',
        message='Error interno del servidor',
        description='Ocurrio un error inesperado al procesar la solicitud'
    )), 500


if __name__ == '__main__':
    app.run(debug=True, port=API_PORT)
