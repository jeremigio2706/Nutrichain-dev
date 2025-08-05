"""
API endpoints para gestión de stock (SOLO CONSULTAS Y REPORTES)

PRINCIPIO DE RESPONSABILIDAD ÚNICA:
- Este módulo SOLO maneja consultas de inventario
- NO tiene endpoints para modificar stock directamente
- Todas las modificaciones se hacen via /api/v1/movimientos

ARQUITECTURA LIMPIA:
- Sin manejo de excepciones repetitivo (usa manejador global)
- Endpoints síncronos (sin async innecesario)
- Responsabilidades claras y separadas
- AUDITABILIDAD: Todo cambio de stock requiere un movimiento registrado
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.stock_service import StockService
from ..dtos.stock_dto import (
    StockResponseDTO,
    StockListDTO,
    StockConsolidadoDTO,
    StockDisponibilidadDTO,
    StockDisponibilidadResponseDTO
)

router = APIRouter(prefix="/stock", tags=["stock"])


def get_stock_service(db: Session = Depends(get_db)) -> StockService:
    """Dependencia para obtener el servicio de stock"""
    return StockService(db)


# =====================================================================
# ENDPOINTS DE CONSULTA ÚNICAMENTE - NIVEL SENIOR
# =====================================================================

@router.get("/", response_model=StockListDTO)
def listar_stock(
    almacen_id: Optional[int] = Query(None, description="Filtrar por almacén"),
    producto_id: Optional[int] = Query(None, description="Filtrar por producto"),
    con_stock: Optional[bool] = Query(None, description="Filtrar solo productos con stock disponible"),
    no_pagination: bool = Query(False, description="Si es true, devuelve todos los resultados sin paginación"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de resultados (ignorado si no_pagination=true)"),
    offset: int = Query(0, ge=0, description="Número de registros a saltar (ignorado si no_pagination=true)"),
    service: StockService = Depends(get_stock_service)
):
    """
    Listar stock con filtros opcionales y paginación configurable
    SOLO LECTURA - Modificaciones via /movimientos
    """
    # Si no_pagination es True, ignorar limit y offset
    final_limit = None if no_pagination else limit
    final_offset = 0 if no_pagination else offset
    
    return service.listar_stock(
        almacen_id=almacen_id,
        producto_id=producto_id,
        con_stock=con_stock,
        limit=final_limit,
        offset=final_offset
    )


@router.get("/{stock_id}", response_model=StockResponseDTO)
def obtener_stock(
    stock_id: int,
    service: StockService = Depends(get_stock_service)
):
    """
    Obtener stock por ID
    SOLO LECTURA - Modificaciones via /movimientos
    """
    return service.obtener_stock(stock_id)


@router.post("/consultar-disponibilidad", response_model=StockDisponibilidadResponseDTO)
def consultar_disponibilidad(
    disponibilidad_data: StockDisponibilidadDTO,
    service: StockService = Depends(get_stock_service)
):
    """
    Consultar disponibilidad de productos en almacenes
    INCLUYE validación con servicio de catálogo
    """
    return service.obtener_disponibilidad(disponibilidad_data)


@router.get("/consolidado/resumen", response_model=List[StockConsolidadoDTO])
def obtener_stock_consolidado(
    almacen_id: Optional[int] = Query(None, description="Filtrar por almacén específico"),
    service: StockService = Depends(get_stock_service)
):
    """
    Obtener resumen consolidado de stock por producto
    SOLO LECTURA - Para reportes y análisis
    """
    return service.obtener_stock_consolidado(almacen_id)

