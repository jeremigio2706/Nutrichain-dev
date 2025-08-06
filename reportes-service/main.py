# ============================================================================
# main.py
#
# Punto de entrada principal para el servicio de reportes. Configura la
# aplicación FastAPI con todos los middlewares, manejadores de excepciones
# y rutas necesarias.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.reportes import router as reportes_router
from app.middleware.exception_handlers import setup_exception_handlers
from app.config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('reportes-service.log')
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("Iniciando servicio de reportes...")
    logger.info(f"Configuración cargada - Servicios externos:")
    logger.info(f"  - Almacén: {settings.almacen_service_url}")
    logger.info(f"  - Tienda: {settings.tienda_service_url}")
    logger.info(f"  - Catálogo: {settings.catalogo_service_url}")
    
    yield
    
    # Shutdown
    logger.info("Cerrando servicio de reportes...")

def create_app() -> FastAPI:
    """Crear y configurar la aplicación FastAPI"""
    
    app = FastAPI(
        title="NutriChain - Servicio de Reportes",
        description="Servicio de consolidación de datos para reportes empresariales",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # En producción especificar dominios específicos
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Configurar manejadores de excepciones
    setup_exception_handlers(app)
    
    # Registrar rutas
    app.include_router(reportes_router)
    
    # Endpoint raíz para verificación básica
    @app.get("/", response_class=JSONResponse)
    async def root():
        """Endpoint raíz del servicio"""
        return {
            "service": "NutriChain Reportes Service",
            "version": "1.0.0",
            "status": "active",
            "endpoints": {
                "docs": "/docs",
                "health": "/api/v1/reportes/health",
                "stock_valorizado": "/api/v1/reportes/stock-valorizado",
                "pedidos_cliente": "/api/v1/reportes/pedidos-cliente/{cliente_id}",
                "trazabilidad": "/api/v1/reportes/trazabilidad-producto/{producto_id}"
            }
        }
    
    # Health check básico
    @app.get("/health", response_class=JSONResponse)
    async def health():
        """Health check básico del servicio"""
        return {
            "status": "healthy",
            "service": "reportes-service",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    
    logger.info("Aplicación FastAPI configurada correctamente")
    return app

# Crear instancia de la aplicación
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Iniciando servidor de desarrollo...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
