"""
Router principal de la API
"""

from fastapi import APIRouter
from .almacenes import router as almacenes_router
from .stock import router as stock_router
from .movimientos import router as movimientos_router

# Router principal que incluye todos los endpoints
api_router = APIRouter()

# Incluir todos los routers
api_router.include_router(almacenes_router)
api_router.include_router(stock_router)
api_router.include_router(movimientos_router)

# Endpoint de salud
@api_router.get("/health")
async def health_check():
    """Endpoint de verificación de salud del servicio"""
    return {
        "status": "healthy",
        "service": "almacen-service",
        "version": "1.0.0"
    }

# Endpoint de información del servicio
@api_router.get("/info")
async def service_info():
    """Información del servicio de almacén"""
    return {
        "service": "almacen-service",
        "description": "Servicio de gestión de almacenes e inventario",
        "version": "1.0.0",
        "endpoints": {
            "almacenes": "Gestión de almacenes",
            "stock": "Gestión de inventario y stock",
            "movimientos": "Gestión de movimientos de inventario"
        },
        "features": [
            "Gestión de múltiples almacenes",
            "Control de stock en tiempo real",
            "Movimientos de entrada, salida y transferencia",
            "Alertas de stock bajo y sin stock",
            "Historial completo de movimientos",
            "Validación de disponibilidad",
            "Reportes y estadísticas"
        ]
    }
