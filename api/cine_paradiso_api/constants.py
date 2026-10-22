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
DB_URL      = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'

TZ_ARG = timezone(timedelta(hours=-3))
OFFSET_ESPERADO = '-03:00'

# 2026-11-18T20:30:00-03:00
FORMATO_FECHA_HORA = '%Y-%m-%dT%H:%M:%S%z'
FORMATO_FECHA      = '%Y-%m-%d'

LIMIT_DEFAULT  = 10
LIMIT_MIN      = 1
LIMIT_MAX      = 100
OFFSET_DEFAULT = 0

ERROR_CODE_INVALID_BODY      = 'invalid.body'
ERROR_CODE_INVALID_FORMAT    = 'invalid.format'
ERROR_CODE_INVALID_MIN_VALUE = 'invalid.min.value'
ERROR_CODE_INVALID_MAX_VALUE = 'invalid.max.value'
ERROR_CODE_UNKNOWN_FIELD     = 'unknown.field'
