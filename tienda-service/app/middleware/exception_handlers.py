# ============================================================================
# exception_handlers.py
#
# Manejadores globales de excepciones para el servicio de tienda. Proporciona
# respuestas consistentes y estructuradas para todas las excepciones del
# sistema, incluyendo errores de negocio y validaciones.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
import logging
from typing import Union

from ..exceptions.api_exceptions import TiendaException

logger = logging.getLogger(__name__)

def setup_exception_handlers(app: FastAPI):
    """Configura los manejadores de excepciones globales"""
    
    @app.exception_handler(TiendaException)
    async def tienda_exception_handler(request: Request, exc: TiendaException):
        """Manejador para excepciones específicas del servicio de tienda"""
        logger.error(f"TiendaException: {exc.message}", extra={"details": exc.details})
        return JSONResponse(
            status_code=400,
            content={
                "error": True,
                "message": exc.message,
                "error_code": exc.error_code,
                "details": exc.details
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Manejador para excepciones HTTP estándar"""
        logger.error(f"HTTPException: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
                "error_code": "HTTP_ERROR"
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Manejador para errores de validación de Pydantic"""
        logger.error(f"ValidationError: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "error": True,
                "message": "Error de validación en los datos enviados",
                "error_code": "VALIDATION_ERROR",
                "details": exc.errors()
            }
        )
    
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """Manejador para errores de integridad de base de datos"""
        logger.error(f"IntegrityError: {str(exc.orig)}")
        
        error_message = "Error de integridad en la base de datos"
        if "unique constraint" in str(exc.orig).lower():
            error_message = "Ya existe un registro con estos datos únicos"
        elif "foreign key constraint" in str(exc.orig).lower():
            error_message = "Referencia a datos que no existen"
        
        return JSONResponse(
            status_code=400,
            content={
                "error": True,
                "message": error_message,
                "error_code": "INTEGRITY_ERROR"
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Manejador para excepciones generales no controladas"""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "Error interno del servidor",
                "error_code": "INTERNAL_SERVER_ERROR"
            }
        )
