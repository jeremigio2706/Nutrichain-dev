# ============================================================================
# envios.py
#
# Endpoints API para gestión de envíos. Proporciona funcionalidades
# completas para la logística de entregas incluyendo programación,
# seguimiento y actualización de estados.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.envio_service import EnvioService
from ..dtos.envio_dto import (
    EnvioCreateDTO, EnvioUpdateDTO,
    EnvioResponseDTO, EnvioListResponseDTO
)

router = APIRouter()

@router.post("/", response_model=EnvioResponseDTO, status_code=201)
def crear_envio(
    envio_data: EnvioCreateDTO,
    db: Session = Depends(get_db)
):
    """Crear un nuevo envío"""
    envio_service = EnvioService(db)
    return envio_service.crear_envio(envio_data)

@router.get("/{envio_id}", response_model=EnvioResponseDTO)
def obtener_envio(
    envio_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un envío por ID"""
    envio_service = EnvioService(db)
    return envio_service.obtener_envio(envio_id)

@router.get("/numero/{numero_envio}", response_model=EnvioResponseDTO)
def obtener_envio_por_numero(
    numero_envio: str,
    db: Session = Depends(get_db)
):
    """Obtener un envío por número"""
    envio_service = EnvioService(db)
    return envio_service.obtener_envio_por_numero(numero_envio)

@router.get("/pedido/{pedido_id}", response_model=List[EnvioResponseDTO])
def obtener_envios_pedido(
    pedido_id: int,
    db: Session = Depends(get_db)
):
    """Obtener todos los envíos de un pedido"""
    envio_service = EnvioService(db)
    return envio_service.obtener_envios_pedido(pedido_id)

@router.get("/", response_model=EnvioListResponseDTO)
def listar_envios(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(100, ge=1, le=1000, description="Tamaño de página"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db)
):
    """Listar envíos con filtros y paginación"""
    envio_service = EnvioService(db)
    return envio_service.listar_envios(page, page_size, estado)

@router.put("/{envio_id}", response_model=EnvioResponseDTO)
def actualizar_envio(
    envio_id: int,
    envio_data: EnvioUpdateDTO,
    db: Session = Depends(get_db)
):
    """Actualizar un envío"""
    envio_service = EnvioService(db)
    return envio_service.actualizar_envio(envio_id, envio_data)

@router.post("/{envio_id}/iniciar-transito", response_model=EnvioResponseDTO)
def iniciar_transito(
    envio_id: int,
    db: Session = Depends(get_db)
):
    """Iniciar tránsito del envío"""
    envio_service = EnvioService(db)
    return envio_service.iniciar_transito(envio_id)

@router.post("/{envio_id}/marcar-entregado", response_model=EnvioResponseDTO)
def marcar_entregado(
    envio_id: int,
    db: Session = Depends(get_db)
):
    """Marcar envío como entregado"""
    envio_service = EnvioService(db)
    return envio_service.marcar_entregado(envio_id)

@router.post("/{envio_id}/cancelar", response_model=EnvioResponseDTO)
def cancelar_envio(
    envio_id: int,
    motivo: str = Query(..., description="Motivo de cancelación"),
    db: Session = Depends(get_db)
):
    """Cancelar un envío"""
    envio_service = EnvioService(db)
    return envio_service.cancelar_envio(envio_id, motivo)

@router.get("/estado/{estado}", response_model=EnvioListResponseDTO)
def obtener_envios_por_estado(
    estado: str,
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(100, ge=1, le=1000, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    """Obtener envíos por estado"""
    envio_service = EnvioService(db)
    return envio_service.listar_envios(page, page_size, estado)
