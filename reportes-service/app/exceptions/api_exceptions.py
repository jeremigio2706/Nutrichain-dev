# ============================================================================
# api_exceptions.py
#
# Excepciones personalizadas para el servicio de reportes. Define
# errores específicos para consolidación de datos, servicios externos
# y generación de reportes.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

class ReportesBaseException(Exception):
    """Excepción base para el servicio de reportes"""
    pass

class ServicioExternoError(ReportesBaseException):
    """Error al comunicarse con servicios externos"""
    
    def __init__(self, servicio: str, mensaje: str):
        self.servicio = servicio
        self.mensaje = mensaje
        super().__init__(f"Error en servicio {servicio}: {mensaje}")

class ReporteError(ReportesBaseException):
    """Error en la generación de reportes"""
    pass

class ParametrosInvalidosError(ReportesBaseException):
    """Error en parámetros de entrada"""
    pass

class DatosInsuficientesError(ReportesBaseException):
    """Error cuando no hay datos suficientes para el reporte"""
    pass

class ConsolidacionError(ReportesBaseException):
    """Error en la consolidación de datos de múltiples servicios"""
    pass
