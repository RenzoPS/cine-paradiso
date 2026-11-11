from io import BytesIO

import segno
from itsdangerous import BadSignature, URLSafeSerializer

from ..constants import API_SECRET_KEY, ERROR_CODE_QR_INVALIDO, QR_ESCALA, QR_SALT, WEB_URL
from ..utils import ErrorAPI


def _crear_serializador():
    # el salt separa estos tokens de los de sesion aunque compartan la clave
    return URLSafeSerializer(API_SECRET_KEY, salt=QR_SALT)


def error_qr_invalido() -> ErrorAPI:
    return ErrorAPI(
        code=ERROR_CODE_QR_INVALIDO,
        message='QR invalido',
        description='El QR no fue emitido por Cine Paradiso o fue modificado',
        status=400,
    )


def generar_token_qr(id_compra: int) -> str:
    return _crear_serializador().dumps({'id_compra': id_compra})


def leer_token_qr(qr_token: str) -> int:
    try:
        return _crear_serializador().loads(qr_token)['id_compra']
    except BadSignature:
        raise error_qr_invalido()


def generar_imagen_qr(qr_token: str) -> BytesIO:
    imagen = BytesIO()
    segno.make(f'{WEB_URL}/admin/validar/{qr_token}').save(imagen, kind='png', scale=QR_ESCALA)
    imagen.seek(0)
    return imagen
