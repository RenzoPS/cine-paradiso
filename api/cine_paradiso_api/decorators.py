from functools import wraps
from flask import request, current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from cine_paradiso_api.utils import ErrorAPI

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
       
        token_encriptado = request.cookies.get('token_sesion')
        
        if not token_encriptado:
            raise ErrorAPI(
                code="auth.missing_cookie",
                message="Sesión no encontrada",
                description="Se requiere iniciar sesión para acceder a esta sección.",
                status=401
            )

        try:
            #Inicializamos el lector usando la clave secreta de la app
            serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            
            #Desencriptamos el carnet en memoria (validez máxima de 24 horas)
            datos_usuario = serializer.loads(token_encriptado, max_age=86400)
            user_role = datos_usuario.get('rol')

           
            if user_role != 'admin':
                raise ErrorAPI(
                    code="auth.access_denied",
                    message="Acceso denegado",
                    description="No tienes los permisos de administrador requeridos para esta acción.",
                    status=403
                )

        #Si el token pasó las 24 horas,lanza esta excepción
        except SignatureExpired:
            raise ErrorAPI(
                code="auth.token_expired",
                message="Sesión expirada",
                description="Tu sesión ha expirado. Por favor, vuelve a iniciar sesión.",
                status=401
            )
            
        #Si alguien modificó la cookie manualmente en el navegador, saltará esto
        except BadSignature:
            raise ErrorAPI(
                code="auth.invalid_token",
                message="Sesión inválida",
                description="El token de sesión es inválido o ha sido manipulado.",
                status=401
            )
        
        return f(*args, **kwargs)
        
    return decorated_function
