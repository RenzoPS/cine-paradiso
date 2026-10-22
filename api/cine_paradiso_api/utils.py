import logging
from datetime import datetime
from re import fullmatch

from .constants import (
    ERROR_CODE_INVALID_BODY,
    ERROR_CODE_INVALID_FORMAT,
    ERROR_CODE_INVALID_MAX_VALUE,
    ERROR_CODE_INVALID_MIN_VALUE,
    ERROR_CODE_UNKNOWN_FIELD,
    FORMATO_FECHA,
    FORMATO_FECHA_HORA,
    OFFSET_ESPERADO,
    TZ_ARG,
)

logger = logging.getLogger(__name__)

PATRON_EMAIL = r'[^@\s]+@[^@\s]+\.[^@\s]+'


def construir_error_api(code: str, message: str, description: str, level: str = 'error') -> dict:
    return {
        'errors': [{
            'code': code,
            'message': message,
            'level': level,
            'description': description
        }]
    }


class ErrorAPI(Exception):

    def __init__(self, code: str, message: str, description: str, status: int = 400):
        super().__init__(message)
        self.code = code
        self.message = message
        self.description = description
        self.status = status

    @property
    def payload(self) -> dict:
        return construir_error_api(self.code, self.message, self.description)


def validar_entero(numero, nombre: str = 'numero') -> int:
    if isinstance(numero, bool):
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_FORMAT,
            message=f"Formato de '{nombre}' invalido",
            description=f"El campo '{nombre}' debe ser un numero entero. Se recibio un booleano"
        )

    if isinstance(numero, int):
        return numero

    try:
        return int(str(numero).strip())
    except (TypeError, ValueError):
        logger.warning(f"Valor numerico invalido: '{numero}' no puede convertirse a entero")

        raise ErrorAPI(
            code=ERROR_CODE_INVALID_FORMAT,
            message=f"Formato de '{nombre}' invalido",
            description=f"El valor '{numero}' no puede convertirse a un numero entero"
        )


def validar_minimo(valor: int, minimo: int, nombre: str) -> int:
    if valor < minimo:
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_MIN_VALUE,
            message='Valor por debajo del minimo permitido',
            description=f"El parametro '{nombre}' debe ser mayor o igual a {minimo}. Se recibio: {valor}"
        )

    return valor


def validar_maximo(valor: int, maximo: int, nombre: str) -> int:
    if valor > maximo:
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_MAX_VALUE,
            message='Valor por encima del maximo permitido',
            description=f"El parametro '{nombre}' debe ser menor o igual a {maximo}. Se recibio: {valor}"
        )

    return valor


def validar_entero_positivo(numero, nombre: str = 'numero') -> int:
    return validar_minimo(validar_entero(numero, nombre), 1, nombre)


def validar_string_no_vacio(valor, nombre: str) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise ErrorAPI(
            code=f'required.{nombre}',
            message=f"Campo requerido: '{nombre}'",
            description=f"El campo '{nombre}' es obligatorio y no puede estar vacio"
        )

    return valor.strip()


def validar_email(valor, nombre: str = 'email') -> str:
    email = validar_string_no_vacio(valor, nombre).lower()

    if not fullmatch(PATRON_EMAIL, email):
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_FORMAT,
            message=f"Formato de '{nombre}' invalido",
            description=f"El valor '{valor}' no es una direccion de correo valida"
        )

    return email


def validar_booleano(valor, nombre: str) -> bool:
    if isinstance(valor, bool):
        return valor

    if isinstance(valor, str) and valor.lower() in ('true', 'false'):
        return valor.lower() == 'true'

    raise ErrorAPI(
        code=ERROR_CODE_INVALID_FORMAT,
        message=f"Formato de '{nombre}' invalido",
        description=f"El campo '{nombre}' solo admite los valores true o false. Se recibio: '{valor}'"
    )


def validar_opcion(valor, opciones: tuple, nombre: str) -> str:
    texto = validar_string_no_vacio(valor, nombre).lower()

    if texto not in opciones:
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_FORMAT,
            message=f"Valor de '{nombre}' invalido",
            description=f"El campo '{nombre}' solo admite: {', '.join(opciones)}. Se recibio: '{valor}'"
        )

    return texto


def validar_cuerpo_no_vacio(body, contexto: str = 'cuerpo') -> dict:
    if not isinstance(body, dict) or not body:
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_BODY,
            message=f"El {contexto} de la solicitud es invalido",
            description=f"El {contexto} debe ser un objeto JSON con al menos un campo y Content-Type application/json"
        )

    return body


def rechazar_campos_desconocidos(datos, permitidos: set, contexto: str = 'cuerpo') -> None:
    desconocidos = set(datos or {}) - set(permitidos)

    if desconocidos:
        raise ErrorAPI(
            code=ERROR_CODE_UNKNOWN_FIELD,
            message='Campos desconocidos',
            description=f"El {contexto} no admite: {', '.join(sorted(desconocidos))}"
        )


def parsear_fecha_hora(valor, nombre: str) -> datetime:
    texto = validar_string_no_vacio(valor, nombre)

    try:
        fecha_hora = datetime.strptime(texto, FORMATO_FECHA_HORA)
    except ValueError:
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_FORMAT,
            message=f"Formato de '{nombre}' invalido",
            description=f"El valor '{texto}' no cumple el formato YYYY-MM-DDTHH:MM:SS{OFFSET_ESPERADO}"
        )

    if fecha_hora.utcoffset() != TZ_ARG.utcoffset(None):
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_FORMAT,
            message=f"Desplazamiento horario invalido en '{nombre}'",
            description=f"El valor '{texto}' debe usar el desplazamiento fijo {OFFSET_ESPERADO}"
        )

    return fecha_hora.replace(tzinfo=None)


def parsear_fecha(valor, nombre: str) -> datetime:
    texto = validar_string_no_vacio(valor, nombre)

    try:
        return datetime.strptime(texto, FORMATO_FECHA)
    except ValueError:
        raise ErrorAPI(
            code=ERROR_CODE_INVALID_FORMAT,
            message=f"Formato de '{nombre}' invalido",
            description=f"El valor '{texto}' no cumple el formato esperado YYYY-MM-DD"
        )


def formatear_fecha_hora(fecha_hora: datetime | None) -> str | None:
    if fecha_hora is None:
        return None

    return fecha_hora.strftime('%Y-%m-%dT%H:%M:%S') + OFFSET_ESPERADO
