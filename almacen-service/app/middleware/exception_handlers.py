"""
Manejadores globales de excepciones para la aplicación FastAPI
Centraliza el manejo de errores y elimina código repetitivo en endpoints
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
import logging
from typing import Union

from ..exceptions.api_exceptions import (
    NotFoundError,
    ValidationError,
    BusinessLogicError,
    AuthenticationError as UnauthorizedError,
    AuthorizationError as ForbiddenError
)

# Configurar logger
logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Configura todos los manejadores de excepciones para la aplicación
    """

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        """Maneja errores de recurso no encontrado (404)"""
        logger.warning(f"NotFoundError en {request.url}: {str(exc)}")
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "message": str(exc),
                "type": "not_found_error",
                "path": str(request.url.path)
            }
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Maneja errores de validación de Pydantic (400) - Solución Senior"""
        logger.warning(f"RequestValidationError en {request.url}: {exc.errors()}")
        
        # Formatear errores de manera profesional
        error_details = []
        for error in exc.errors():
            field = " -> ".join(str(x) for x in error["loc"])
            error_details.append(f"{field}: {error['msg']}")
        
        return JSONResponse(
            status_code=400,
            content={
                "error": "Validation Error",
                "message": "Los datos enviados no son válidos",
                "details": error_details,
                "type": "validation_error",
                "path": str(request.url.path)
            }
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
        """Maneja errores de validación customizados (400)"""
        logger.warning(f"ValidationError en {request.url}: {str(exc)}")
        return JSONResponse(
            status_code=400,
            content={
                "error": "Validation Error",
                "message": str(exc),
                "type": "validation_error",
                "path": str(request.url.path)
            }
        )

    @app.exception_handler(BusinessLogicError)
    async def business_logic_error_handler(request: Request, exc: BusinessLogicError) -> JSONResponse:
        """Maneja errores de lógica de negocio (422)"""
        logger.warning(f"BusinessLogicError en {request.url}: {str(exc)}")
        return JSONResponse(
            status_code=422,
            content={
                "error": "Business Logic Error",
                "message": str(exc),
                "type": "business_logic_error",
                "path": str(request.url.path)
            }
        )

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_error_handler(request: Request, exc: UnauthorizedError) -> JSONResponse:
        """Maneja errores de autenticación (401)"""
        logger.warning(f"UnauthorizedError en {request.url}: {str(exc)}")
        return JSONResponse(
            status_code=401,
            content={
                "error": "Unauthorized",
                "message": str(exc),
                "type": "unauthorized_error",
                "path": str(request.url.path)
            }
        )

    @app.exception_handler(ForbiddenError)
    async def forbidden_error_handler(request: Request, exc: ForbiddenError) -> JSONResponse:
        """Maneja errores de autorización (403)"""
        logger.warning(f"ForbiddenError en {request.url}: {str(exc)}")
        return JSONResponse(
            status_code=403,
            content={
                "error": "Forbidden",
                "message": str(exc),
                "type": "forbidden_error",
                "path": str(request.url.path)
            }
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """Maneja errores de valor (400)"""
        logger.warning(f"ValueError en {request.url}: {str(exc)}")
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid Value",
                "message": str(exc),
                "type": "value_error",
                "path": str(request.url.path)
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Maneja todas las demás excepciones no previstas (500)"""
        logger.error(f"Error interno en {request.url}: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "Ha ocurrido un error interno. Por favor contacte al administrador.",
                "type": "internal_server_error",
                "path": str(request.url.path)
            }
        )

    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """Maneja HTTPExceptions de FastAPI con formato consistente"""
        logger.warning(f"HTTPException en {request.url}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Error",
                "message": exc.detail,
                "type": "http_exception",
                "path": str(request.url.path)
            }
        )
