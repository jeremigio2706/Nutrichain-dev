# ============================================================================
# exception_handlers.py
#
# Manejadores de excepciones para el servicio de reportes. Proporciona
# respuestas consistentes y logging apropiado para diferentes tipos
# de errores en la consolidación de datos.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..exceptions.api_exceptions import (
    ReportesBaseException, ServicioExternoError, ReporteError,
    ParametrosInvalidosError, DatosInsuficientesError, ConsolidacionError
)

logger = logging.getLogger(__name__)

def setup_exception_handlers(app):
    """Configurar manejadores de excepciones globales"""
    
    @app.exception_handler(ServicioExternoError)
    async def servicio_externo_error_handler(request: Request, exc: ServicioExternoError):
        """Manejar errores de servicios externos"""
        logger.error(f"Error en servicio externo {exc.servicio}: {exc.mensaje}")
        return JSONResponse(
            status_code=503,
            content={
                "error": True,
                "message": f"Servicio {exc.servicio} no disponible",
                "error_code": "SERVICIO_NO_DISPONIBLE",
                "details": {
                    "servicio": exc.servicio,
                    "error_message": exc.mensaje
                }
            }
        )
    
    @app.exception_handler(ReporteError)
    async def reporte_error_handler(request: Request, exc: ReporteError):
        """Manejar errores en generación de reportes"""
        logger.error(f"Error generando reporte: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "Error interno generando reporte",
                "error_code": "REPORTE_ERROR",
                "details": {"error_message": str(exc)}
            }
        )
    
    @app.exception_handler(ParametrosInvalidosError)
    async def parametros_invalidos_handler(request: Request, exc: ParametrosInvalidosError):
        """Manejar errores de parámetros inválidos"""
        logger.warning(f"Parámetros inválidos: {str(exc)}")
        return JSONResponse(
            status_code=400,
            content={
                "error": True,
                "message": "Parámetros de entrada inválidos",
                "error_code": "PARAMETROS_INVALIDOS",
                "details": {"error_message": str(exc)}
            }
        )
    
    @app.exception_handler(DatosInsuficientesError)
    async def datos_insuficientes_handler(request: Request, exc: DatosInsuficientesError):
        """Manejar errores de datos insuficientes"""
        logger.info(f"Datos insuficientes para reporte: {str(exc)}")
        return JSONResponse(
            status_code=404,
            content={
                "error": True,
                "message": "No hay datos suficientes para generar el reporte",
                "error_code": "DATOS_INSUFICIENTES",
                "details": {"error_message": str(exc)}
            }
        )
    
    @app.exception_handler(ConsolidacionError)
    async def consolidacion_error_handler(request: Request, exc: ConsolidacionError):
        """Manejar errores de consolidación"""
        logger.error(f"Error en consolidación de datos: {str(exc)}")
        return JSONResponse(
            status_code=502,
            content={
                "error": True,
                "message": "Error consolidando datos de múltiples servicios",
                "error_code": "CONSOLIDACION_ERROR",
                "details": {"error_message": str(exc)}
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Manejar errores de validación de Pydantic"""
        logger.warning(f"Error de validación: {str(exc)}")
        return JSONResponse(
            status_code=422,
            content={
                "error": True,
                "message": "Error de validación en los datos enviados",
                "error_code": "VALIDATION_ERROR",
                "details": [str(error) for error in exc.errors()]
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Manejar excepciones HTTP estándar"""
        logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
                "error_code": "HTTP_ERROR"
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Manejar excepciones generales no capturadas"""
        logger.error(f"Error no manejado: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "Error interno del servidor",
                "error_code": "INTERNAL_SERVER_ERROR"
            }
        )
