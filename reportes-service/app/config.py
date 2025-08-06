# ============================================================================
# config.py
#
# Configuración global del servicio de reportes. Define URLs de
# microservicios externos, configuración de conexiones y parámetros
# para la consolidación de datos.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    app_name: str = "NutriChain Reportes Service"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    allowed_origins: List[str] = ["*"]
    
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    almacen_service_url: str = os.getenv(
        "ALMACEN_SERVICE_URL", 
        "http://localhost:8001"
    )
    
    tienda_service_url: str = os.getenv(
        "TIENDA_SERVICE_URL", 
        "http://localhost:8003"
    )
    
    catalogo_service_url: str = os.getenv(
        "CATALOGO_SERVICE_URL", 
        "http://localhost:8000"
    )
    
    secret_key: str = os.getenv("SECRET_KEY", "reportes-secret-key-change-in-production")
    
    cache_ttl_seconds: int = 300
    max_concurrent_requests: int = 50
    request_timeout_seconds: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
