# ============================================================================
# main.py
#
# Punto de entrada principal del servicio de tienda. Configura la aplicación
# FastAPI con todas las rutas, middleware y manejadores de excepciones.
# Este servicio orquesta el ciclo de vida de pedidos y gestiona las
# comunicaciones con otros microservicios.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.config import settings
from app.database import get_db, engine, Base
from app.middleware.exception_handlers import setup_exception_handlers

from app.api.clientes import router as clientes_router
from app.api.pedidos import router as pedidos_router
from app.api.envios import router as envios_router
from app.api.devoluciones import router as devoluciones_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NutriChain Logistics - Tienda Service",
    description="Servicio para gestión de clientes, pedidos, envíos y devoluciones",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

setup_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clientes_router, prefix="/clientes", tags=["clientes"])
app.include_router(pedidos_router, prefix="/pedidos", tags=["pedidos"])
app.include_router(envios_router, prefix="/envios", tags=["envios"])
app.include_router(devoluciones_router, prefix="/devoluciones", tags=["devoluciones"])

@app.get("/")
async def root():
    return {"message": "NutriChain Tienda Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug
    )
