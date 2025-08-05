"""
Configuración del servicio de almacén
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Base de datos
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:password@localhost:5432/almacen_db"
    )
    
    # Configuración del servidor
    app_name: str = "NutriChain Almacén Service"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Configuración de CORS
    allowed_origins: list = ["*"]
    
    # Configuración de logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Configuración de stock
    stock_minimo_default: float = 10.0
    stock_critico_threshold: float = 5.0
    
    # Configuración de API externa (catalogo-service)
    catalogo_service_url: str = os.getenv(
        "CATALOGO_SERVICE_URL", 
        "http://localhost:8000"  # Puerto correcto del catálogo
    )
    
    # Configuración de autenticación (para futuras implementaciones)
    secret_key: str = os.getenv("SECRET_KEY", "almacen-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Configuración de Redis (para caché, si se implementa)
    redis_url: Optional[str] = os.getenv("REDIS_URL", None)
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instancia global de configuración
settings = Settings()
