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

ERROR_CODE_AUTH_TOKEN_MISSING = 'auth.token.missing'
ERROR_CODE_AUTH_TOKEN_EXPIRED = 'auth.token.expired'
ERROR_CODE_AUTH_TOKEN_INVALID = 'auth.token.invalid'
ERROR_CODE_AUTH_ACCESS_DENIED = 'auth.access.denied'

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

HORAS_LIMITE_CANCELACION = 24

ERROR_CODE_COMPRA_NOT_FOUND      = 'compra.not.found'
ERROR_CODE_COMPRA_VENCIDA        = 'compra.vencida'
ERROR_CODE_COMPRA_NO_CONFIRMABLE = 'compra.no.confirmable'
ERROR_CODE_COMPRA_SIN_FACTURA    = 'compra.sin.factura'