import os
from datetime import timedelta, timezone

from dotenv import load_dotenv

load_dotenv()

BASE_URL = '/cine_paradiso_api'
API_PORT = int(os.getenv('API_PORT', '5000'))

DB_HOST     = os.getenv('DB_HOST', 'localhost')
DB_PORT     = int(os.getenv('DB_PORT', '3306'))
DB_USER     = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
DB_NAME     = os.getenv('DB_NAME', 'cine_paradiso')
DB_URL      = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

TMDB_API_KEY = os.getenv('TMDB_API_KEY', '').strip()
TMDB_API_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_API_URL = f'{TMDB_API_BASE_URL}/search/movie'
TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'
TMDB_LANGUAGE = 'es-AR'
TMDB_TIMEOUT = 5

TZ_ARG = timezone(timedelta(hours=-3))
OFFSET_ESPERADO = '-03:00'

# 2026-11-18T20:30:00-03:00
FORMATO_FECHA_HORA = '%Y-%m-%dT%H:%M:%S%z'
FORMATO_FECHA      = '%Y-%m-%d'

LIMIT_DEFAULT  = 10
LIMIT_MIN      = 1
LIMIT_MAX      = 100
OFFSET_DEFAULT = 0

API_SECRET_KEY          = os.getenv('API_SECRET_KEY')
TOKEN_COOKIE_NOMBRE     = 'token_sesion'
TOKEN_DURACION_SEGUNDOS = 86400
ROL_ADMIN               = 'admin'
ROL_CLIENTE             = 'cliente'

NOMBRE_MAX_LARGO = 80
APELLIDO_MAX_LARGO = 80
EMAIL_MAX_LARGO = 120
CONTRASENA_MIN_LARGO = 8
CONTRASENA_MAX_LARGO = 128

CAMPOS_REGISTRO = frozenset({'nombre','apellido','email','contrasena',})
CAMPOS_LOGIN = frozenset({'email','contrasena',})

ERROR_CODE_AUTH_TOKEN_MISSING = 'auth.token.missing'
ERROR_CODE_AUTH_TOKEN_EXPIRED = 'auth.token.expired'
ERROR_CODE_AUTH_TOKEN_INVALID = 'auth.token.invalid'
ERROR_CODE_AUTH_ACCESS_DENIED = 'auth.access.denied'
ERROR_CODE_AUTH_CREDENCIALES_INVALIDAS = 'auth.credentials.invalid'
ERROR_CODE_USUARIO_EMAIL_DUPLICADO = 'usuario.email.duplicated'
ERROR_CODE_USUARIO_NO_ENCONTRADO = 'usuario.not.found'

ERROR_CODE_INVALID_BODY      = 'invalid.body'
ERROR_CODE_INVALID_FORMAT    = 'invalid.format'
ERROR_CODE_INVALID_MIN_VALUE = 'invalid.min.value'
ERROR_CODE_INVALID_MAX_VALUE = 'invalid.max.value'
ERROR_CODE_UNKNOWN_FIELD     = 'unknown.field'



WEB_URL = os.getenv('WEB_URL', 'http://localhost:5001')

MAIL_HOST     = os.getenv('MAIL_HOST', '')
MAIL_PORT     = int(os.getenv('MAIL_PORT', '587'))
MAIL_USER     = os.getenv('MAIL_USER', '')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
MAIL_FROM     = os.getenv('MAIL_FROM', '')

ESTADO_PENDIENTE = 'pendiente'
ESTADO_PAGADA    = 'pagada'
ESTADO_VENCIDA   = 'vencida'
ESTADO_USADA     = 'usada'
ESTADO_CANCELADA = 'cancelada'

QR_SALT   = 'qr-compra'
QR_ESCALA = 8

HORAS_LIMITE_CANCELACION = 24

ERROR_CODE_COMPRA_NOT_FOUND      = 'compra.not.found'
ERROR_CODE_COMPRA_VENCIDA        = 'compra.vencida'
ERROR_CODE_COMPRA_NO_CONFIRMABLE = 'compra.no.confirmable'
ERROR_CODE_COMPRA_SIN_FACTURA    = 'compra.sin.factura'

ERROR_CODE_QR_INVALIDO     = 'qr.invalid'
ERROR_CODE_QR_SIN_EMITIR   = 'qr.not.issued'
ERROR_CODE_QR_UTILIZADO    = 'qr.already.used'
ERROR_CODE_QR_CANCELADO    = 'qr.cancelled'
ERROR_CODE_QR_NO_PAGADO    = 'qr.not.paid'
ERROR_CODE_QR_OTRA_FUNCION = 'qr.wrong.function'
ERROR_CODE_QR_OTRO_DIA     = 'qr.wrong.date'
