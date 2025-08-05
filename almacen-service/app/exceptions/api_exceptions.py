"""
Excepciones personalizadas para la API
"""


class APIException(Exception):
    """Excepción base para errores de la API"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(APIException):
    """Error cuando un recurso no es encontrado"""
    def __init__(self, message: str = "Recurso no encontrado"):
        super().__init__(message, 404)


class ValidationError(APIException):
    """Error de validación de datos"""
    def __init__(self, message: str = "Error de validación"):
        super().__init__(message, 400)


class BusinessLogicError(APIException):
    """Error de lógica de negocio"""
    def __init__(self, message: str = "Error de lógica de negocio"):
        super().__init__(message, 409)


class AuthenticationError(APIException):
    """Error de autenticación"""
    def __init__(self, message: str = "Error de autenticación"):
        super().__init__(message, 401)


class AuthorizationError(APIException):
    """Error de autorización"""
    def __init__(self, message: str = "No autorizado"):
        super().__init__(message, 403)


class DatabaseError(APIException):
    """Error de base de datos"""
    def __init__(self, message: str = "Error de base de datos"):
        super().__init__(message, 500)


class ExternalServiceError(APIException):
    """Error en servicio externo"""
    def __init__(self, message: str = "Error en servicio externo"):
        super().__init__(message, 503)
