"""
Módulo de excepciones personalizadas
"""

from .api_exceptions import (
    APIException,
    NotFoundError,
    ValidationError,
    BusinessLogicError,
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
    ExternalServiceError
)

__all__ = [
    "APIException",
    "NotFoundError",
    "ValidationError",
    "BusinessLogicError",
    "AuthenticationError",
    "AuthorizationError",
    "DatabaseError",
    "ExternalServiceError"
]
