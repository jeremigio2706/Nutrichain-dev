# ============================================================================
# config.py
#
# Configuración global del servicio de tienda. Define parámetros de conexión
# a base de datos, URLs de servicios externos, configuración de Redis para
# colas de pedidos y otras configuraciones de la aplicación.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

import os
from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:password@localhost:5432/tienda_db"
    )
    
    app_name: str = "NutriChain Tienda Service"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    allowed_origins: List[str] = ["*"]
    
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    almacen_service_url: str = os.getenv(
        "ALMACEN_SERVICE_URL", 
        "http://localhost:8001"
    )
    
    catalogo_service_url: str = os.getenv(
        "CATALOGO_SERVICE_URL", 
        "http://localhost:8000"
    )
    
    secret_key: str = os.getenv("SECRET_KEY", "tienda-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    limite_credito_default: float = 1000000.0
    descuento_maximo_porcentaje: float = 50.0
    
    numero_pedido_prefix: str = "PED"
    numero_envio_prefix: str = "ENV"
    numero_devolucion_prefix: str = "DEV"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
