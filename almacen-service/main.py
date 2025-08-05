"""
NutriChain Logistics - Servicio de Almacén
FastAPI service para gestión de almacenes, stock y movimientos de inventario

ARQUITECTURA SENIOR:
- Manejo global de excepciones (sin try/catch repetitivo)
- Separación clara de responsabilidades
- Endpoints síncronos optimizados
- Única fuente de verdad para modificaciones de stock
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn

# Configuración
from app.config import settings
from app.database import get_db, engine, Base

# Middleware de manejo de excepciones
from app.middleware.exception_handlers import setup_exception_handlers

# Routers
from app.api.almacenes import router as almacenes_router
from app.api.stock import router as stock_router
from app.api.movimientos import router as movimientos_router

# Crear tablas
Base.metadata.create_all(bind=engine)

# Inicializar FastAPI
app = FastAPI(
    title="NutriChain Logistics - Almacén Service",
    description="""
    Servicio para gestión de almacenes, stock y movimientos de inventario
    
    ARQUITECTURA REFACTORIZADA:
    - StockService: SOLO consultas y reportes
    - MovimientoService: ÚNICA fuente de verdad para modificaciones
    - Manejo global de excepciones
    - Endpoints síncronos optimizados
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar manejadores de excepciones globales
setup_exception_handlers(app)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción usar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(almacenes_router, prefix="/api/v1")
app.include_router(stock_router, prefix="/api/v1")
app.include_router(movimientos_router, prefix="/api/v1")


@app.get("/")
def root():
    """Endpoint raíz del servicio - REFACTORIZADO"""
    return {
        "service": "NutriChain Logistics - Almacén Service",
        "version": "2.0.0 - REFACTORIZADO",
        "status": "active",
        "architecture": {
            "pattern": "Clean Architecture",
            "principles": [
                "Single Responsibility",
                "DRY (Don't Repeat Yourself)", 
                "Single Source of Truth",
                "Global Exception Handling"
            ]
        },
        "endpoints": {
            "almacenes": "/api/v1/almacenes",
            "stock_queries": "/api/v1/stock (SOLO CONSULTAS)",
            "inventory_movements": "/api/v1/movimientos (ÚNICA FUENTE PARA MODIFICACIONES)",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "refactoring_highlights": [
            "Eliminados endpoints duplicados de stock/entrada y stock/salida",
            "StockService solo maneja consultas y reportes",
            "MovimientoService es la única fuente de verdad para modificaciones",
            "Manejo global de excepciones (sin try/catch repetitivo)",
            "Endpoints síncronos (eliminado async innecesario)"
        ]
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check del servicio - SIN MANEJO MANUAL DE EXCEPCIONES"""
    # Las excepciones las maneja el handler global automáticamente
    from sqlalchemy import text
    db.execute(text("SELECT 1"))
    
    return {
        "status": "healthy",
        "database": "connected",
        "service": "almacen-service-refactored",
        "architecture": "clean"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )