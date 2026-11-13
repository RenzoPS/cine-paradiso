import os

from dotenv import load_dotenv

load_dotenv()

WEB_PORT = int(os.getenv('WEB_PORT', '5001'))

SECRET_KEY = os.getenv('WEB_SECRET_KEY', 'solo-para-desarrollo')

API_URL = os.getenv('API_URL', 'http://localhost:5000/cine_paradiso_api')

# Listas estáticas para la cartelera y filtros iniciales
GENEROS_DISPONIBLES = [
    'Todos', 'Drama', 'Comedia', 'Acción', 'Ciencia Ficción', 'Suspenso', 'Terror', 'Aventura', 'Romance'
]

SUCURSALES_DISPONIBLES = [
    {'id': '', 'nombre': 'Todas las sedes'},
    {'id': '1', 'nombre': 'Sucursal Centro'},
    {'id': '2', 'nombre': 'Sucursal Belgrano'},
    {'id': '3', 'nombre': 'Sucursal Recoleta'}
]

PELICULAS = []

TOKEN_COOKIE_NOMBRE = 'token_sesion'
ROL_ADMIN = 'admin'

API_TIMEOUT_SEGUNDOS = 10

HORAS_LIMITE_CANCELACION = 24