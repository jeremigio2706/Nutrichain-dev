"""
API endpoints para gestión de movimientos de inventario

PRINCIPIO DE RESPONSABILIDAD ÚNICA:
- Este es el ÚNICO módulo autorizado para modificar stock
- Centraliza toda la lógica de movimientos
- Garantiza auditoría completa y consistencia

ARQUITECTURA LIMPIA:
- Sin manejo de excepciones repetitivo (usa manejador global)
- Endpoints síncronos (sin async innecesario)
- Única fuente de verdad para modificaciones de inventario
"""

from typing import List, Optional, Dict, Any, Union
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.movimiento_service import MovimientoService
from ..dtos.movimiento_dto import (
    MovimientoEntradaDTO,
    MovimientoSalidaDTO,
    MovimientoTransferenciaDTO,
    MovimientoAjusteInicialDTO,
    MovimientoResponseDTO,
    MovimientoListDTO,
    MovimientosEntradaDTO,
    MovimientosSalidaDTO,
    MovimientosMultipleResponseDTO,
    TipoMovimientoEnum
)

router = APIRouter(prefix="/movimientos", tags=["movimientos"])


def get_movimiento_service(db: Session = Depends(get_db)) -> MovimientoService:
    """Dependencia para obtener el servicio de movimientos"""
    return MovimientoService(db)


# =====================================================================
# ENDPOINTS PARA MODIFICAR STOCK (ÚNICA FUENTE DE VERDAD)
# =====================================================================

@router.post("/entrada")
def crear_movimiento_entrada(
    request_data: Union[MovimientoEntradaDTO, MovimientosEntradaDTO],
    service: MovimientoService = Depends(get_movimiento_service)
):
    """
    Crear uno o múltiples movimientos de entrada de inventario
    
    Acepta:
    - MovimientoEntradaDTO: Para un solo movimiento
    - MovimientosEntradaDTO: Para múltiples movimientos
    
    Validaciones automáticas:
    - Existencia del producto en catálogo
    - Estado activo del producto
    - Existencia y estado activo del almacén
    - Integridad de datos y transacciones atómicas
    """
    # Determinar si es operación individual o múltiple
    if hasattr(request_data, 'movimientos'):
        # Es una operación múltiple
        return service.crear_movimientos_entrada_multiple(request_data.movimientos)
    else:
        # Es una operación individual
        return service.crear_movimiento_entrada(request_data)


@router.post("/salida")
def crear_movimiento_salida(
    request_data: Union[MovimientoSalidaDTO, MovimientosSalidaDTO],
    service: MovimientoService = Depends(get_movimiento_service)
):
    """
    Crear uno o múltiples movimientos de salida de inventario
    
    Acepta:
    - MovimientoSalidaDTO: Para un solo movimiento
    - MovimientosSalidaDTO: Para múltiples movimientos
    
    Validaciones automáticas:
    - Existencia del producto en catálogo
    - Estado activo del producto
    - Existencia y estado activo del almacén
    - Disponibilidad de stock suficiente
    - Integridad de datos y transacciones atómicas
    """
    # Determinar si es operación individual o múltiple
    if hasattr(request_data, 'movimientos'):
        # Es una operación múltiple
        return service.crear_movimientos_salida_multiple(request_data.movimientos)
    else:
        # Es una operación individual
        return service.crear_movimiento_salida(request_data)


@router.post("/transferencia", response_model=MovimientoResponseDTO, status_code=status.HTTP_201_CREATED)
def crear_movimiento_transferencia(
    movimiento_data: MovimientoTransferenciaDTO,
    service: MovimientoService = Depends(get_movimiento_service)
):
    """
    Crear movimiento de transferencia entre almacenes
    OPERACIÓN COMPLEJA: Actualiza stock en origen y destino
    """
    return service.crear_movimiento_transferencia(movimiento_data)


@router.post("/ajuste-inicial", response_model=MovimientoResponseDTO, status_code=status.HTTP_201_CREATED)
def crear_stock_inicial_auditado(
    ajuste_data: MovimientoAjusteInicialDTO,
    service: MovimientoService = Depends(get_movimiento_service)
):
    """
    MÉTODO NIVEL SENIOR: Crear stock inicial de forma completamente auditada
    
    Este es el reemplazo SEGURO para crear stock directamente.
    Todo stock inicial queda registrado con un movimiento de ajuste.
    
    VALIDACIONES AUTOMÁTICAS:
    - Verificación de existencia del producto en Catálogo
    - Prevención de stock duplicado
    - Auditoría completa del stock inicial
    """
    return service.crear_stock_inicial_auditado(ajuste_data)


# =====================================================================
# ENDPOINTS DE CONSULTA
# =====================================================================

@router.get("/", response_model=MovimientoListDTO)
def listar_movimientos(
    skip: int = Query(0, ge=0, description="Número de registros a saltar (ignorado si no_pagination=true)"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar (ignorado si no_pagination=true)"),
    no_pagination: bool = Query(False, description="Si es true, devuelve todos los resultados sin paginación"),
    almacen_id: Optional[int] = Query(None, description="Filtrar por ID de almacén"),
    tipo_movimiento: Optional[TipoMovimientoEnum] = Query(None, description="Filtrar por tipo de movimiento"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    service: MovimientoService = Depends(get_movimiento_service)
):
    """Listar movimientos con filtros opcionales y paginación configurable"""
    # Construir filtros
    filtros = {}
    if almacen_id:
        filtros['almacen_id'] = almacen_id
    if tipo_movimiento:
        filtros['tipo_movimiento'] = tipo_movimiento
    if fecha_inicio:
        filtros['fecha_inicio'] = fecha_inicio
    if fecha_fin:
        filtros['fecha_fin'] = fecha_fin
    
    # Si no_pagination es True, ignorar skip y limit
    final_skip = 0 if no_pagination else skip
    final_limit = None if no_pagination else limit
    
    return service.listar_movimientos(
        skip=final_skip,
        limit=final_limit,
        filtros=filtros if filtros else None
    )


@router.get("/{movimiento_id}", response_model=MovimientoResponseDTO)
def obtener_movimiento(
    movimiento_id: int,
    service: MovimientoService = Depends(get_movimiento_service)
):
    """Obtener un movimiento específico por ID"""
    return service.obtener_movimiento(movimiento_id)


@router.get("/almacen/{almacen_id}", response_model=MovimientoListDTO)
def obtener_movimientos_por_almacen(
    almacen_id: int,
    skip: int = Query(0, ge=0, description="Número de registros a saltar (ignorado si no_pagination=true)"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar (ignorado si no_pagination=true)"),
    no_pagination: bool = Query(False, description="Si es true, devuelve todos los resultados sin paginación"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    tipo_movimiento: Optional[TipoMovimientoEnum] = Query(None, description="Filtrar por tipo de movimiento"),
    service: MovimientoService = Depends(get_movimiento_service)
):
    """Obtener movimientos por almacén con filtros opcionales y paginación configurable"""
    # Si no_pagination es True, ignorar skip y limit
    final_skip = 0 if no_pagination else skip
    final_limit = None if no_pagination else limit
    
    return service.obtener_movimientos_por_almacen(
        almacen_id=almacen_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        tipo_movimiento=tipo_movimiento,
        skip=final_skip,
        limit=final_limit
    )


@router.get("/reporte/movimientos", response_model=Dict[str, Any])
def obtener_reporte_movimientos(
    fecha_inicio: date = Query(..., description="Fecha de inicio del reporte (YYYY-MM-DD)"),
    fecha_fin: date = Query(..., description="Fecha de fin del reporte (YYYY-MM-DD)"),
    almacen_id: Optional[int] = Query(None, description="Filtrar por ID de almacén"),
    tipo_movimiento: Optional[TipoMovimientoEnum] = Query(None, description="Filtrar por tipo de movimiento"),
    service: MovimientoService = Depends(get_movimiento_service)
):
    """Generar reporte de movimientos por período"""
    return service.obtener_reporte_movimientos(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        almacen_id=almacen_id,
        tipo_movimiento=tipo_movimiento
    )
