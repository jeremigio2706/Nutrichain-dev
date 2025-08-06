# ============================================================================
# devoluciones.py
#
# Endpoints API para gestión de devoluciones. Implementa el flujo completo
# del proceso de devoluciones incluyendo inspección, aprobación y
# reintegración de inventario.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Header
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.devolucion_service import DevolucionService
from ..dtos.devolucion_dto import (
    DevolucionCreateDTO, DevolucionUpdateDTO,
    DevolucionResponseDTO, DevolucionListResponseDTO
)

router = APIRouter()

@router.post("/", response_model=DevolucionResponseDTO, status_code=201)
def crear_devolucion(
    devolucion_data: DevolucionCreateDTO,
    db: Session = Depends(get_db)
):
    """Crear una nueva devolución"""
    devolucion_service = DevolucionService(db)
    return devolucion_service.crear_devolucion(devolucion_data)

@router.get("/{devolucion_id}", response_model=DevolucionResponseDTO)
def obtener_devolucion(
    devolucion_id: int,
    db: Session = Depends(get_db)
):
    """Obtener una devolución por ID"""
    devolucion_service = DevolucionService(db)
    return devolucion_service.obtener_devolucion(devolucion_id)

@router.get("/numero/{numero_devolucion}", response_model=DevolucionResponseDTO)
def obtener_devolucion_por_numero(
    numero_devolucion: str,
    db: Session = Depends(get_db)
):
    """Obtener una devolución por número"""
    devolucion_service = DevolucionService(db)
    return devolucion_service.obtener_devolucion_por_numero(numero_devolucion)

@router.get("/pedido/{pedido_id}", response_model=List[DevolucionResponseDTO])
def obtener_devoluciones_pedido(
    pedido_id: int,
    db: Session = Depends(get_db)
):
    """Obtener todas las devoluciones de un pedido"""
    devolucion_service = DevolucionService(db)
    return devolucion_service.obtener_devoluciones_pedido(pedido_id)

@router.get("/", response_model=DevolucionListResponseDTO)
def listar_devoluciones(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(100, ge=1, le=1000, description="Tamaño de página"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db)
):
    """Listar devoluciones con filtros y paginación"""
    devolucion_service = DevolucionService(db)
    return devolucion_service.listar_devoluciones(page, page_size, estado)

@router.put("/{devolucion_id}", response_model=DevolucionResponseDTO)
def actualizar_devolucion(
    devolucion_id: int,
    devolucion_data: DevolucionUpdateDTO,
    db: Session = Depends(get_db)
):
    """Actualizar una devolución"""
    devolucion_service = DevolucionService(db)
    return devolucion_service.actualizar_devolucion(devolucion_id, devolucion_data)

@router.post("/{devolucion_id}/inspeccionar", response_model=DevolucionResponseDTO)
def inspeccionar_devolucion(
    devolucion_id: int,
    usuario: str = Header(..., alias="X-Usuario"),
    db: Session = Depends(get_db)
):
    """Marcar devolución como inspeccionada"""
    devolucion_service = DevolucionService(db)
    return devolucion_service.inspeccionar_devolucion(devolucion_id, usuario)

@router.post("/{devolucion_id}/aprobar", response_model=DevolucionResponseDTO)
async def aprobar_devolucion(
    devolucion_id: int,
    usuario: str = Header(..., alias="X-Usuario"),
    db: Session = Depends(get_db)
):
    """Aprobar devolución y procesar reintegro de inventario"""
    devolucion_service = DevolucionService(db)
    return await devolucion_service.aprobar_devolucion(devolucion_id, usuario)

@router.post("/{devolucion_id}/rechazar", response_model=DevolucionResponseDTO)
def rechazar_devolucion(
    devolucion_id: int,
    motivo: str = Query(..., description="Motivo del rechazo"),
    usuario: str = Header(..., alias="X-Usuario"),
    db: Session = Depends(get_db)
):
    """Rechazar una devolución"""
    devolucion_service = DevolucionService(db)
    return devolucion_service.rechazar_devolucion(devolucion_id, usuario, motivo)

@router.post("/{devolucion_id}/procesar", response_model=DevolucionResponseDTO)
async def procesar_devolucion(
    devolucion_id: int,
    usuario: str = Header(..., alias="X-Usuario"),
    db: Session = Depends(get_db)
):
    """Procesar completamente una devolución aprobada"""
    devolucion_service = DevolucionService(db)
    return await devolucion_service.procesar_devolucion(devolucion_id, usuario)

@router.get("/estado/{estado}", response_model=DevolucionListResponseDTO)
def obtener_devoluciones_por_estado(
    estado: str,
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(100, ge=1, le=1000, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    """Obtener devoluciones por estado"""
    devolucion_service = DevolucionService(db)
    return devolucion_service.listar_devoluciones(page, page_size, estado)
