# ============================================================================
# pedidos.py
#
# Endpoints API para gestión de pedidos. Implementa el flujo completo
# del ciclo de vida de pedidos incluyendo creación, confirmación,
# cancelación y seguimiento de estados.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from typing import Optional
from fastapi import APIRouter, Depends, Query, Header
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.pedido_service import PedidoService
from ..dtos.pedido_dto import (
    PedidoCreateDTO, PedidoUpdateDTO, PedidoConfirmarDTO,
    PedidoResponseDTO, PedidoListResponseDTO
)

router = APIRouter()

@router.post("/", response_model=PedidoResponseDTO, status_code=201)
async def crear_pedido(
    pedido_data: PedidoCreateDTO,
    usuario_creacion: str = Header(..., alias="X-Usuario"),
    db: Session = Depends(get_db)
):
    """Crear un nuevo pedido con validaciones y reservas de stock"""
    pedido_service = PedidoService(db)
    return await pedido_service.crear_pedido(pedido_data, usuario_creacion)

@router.get("/{pedido_id}", response_model=PedidoResponseDTO)
def obtener_pedido(
    pedido_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un pedido por ID"""
    pedido_service = PedidoService(db)
    return pedido_service.obtener_pedido(pedido_id)

@router.get("/numero/{numero_pedido}", response_model=PedidoResponseDTO)
def obtener_pedido_por_numero(
    numero_pedido: str,
    db: Session = Depends(get_db)
):
    """Obtener un pedido por número"""
    pedido_service = PedidoService(db)
    return pedido_service.obtener_pedido_por_numero(numero_pedido)

@router.get("/", response_model=PedidoListResponseDTO)
def listar_pedidos(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(100, ge=1, le=1000, description="Tamaño de página"),
    cliente_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db)
):
    """Listar pedidos con filtros y paginación"""
    pedido_service = PedidoService(db)
    return pedido_service.listar_pedidos(page, page_size, cliente_id, estado)

@router.put("/{pedido_id}", response_model=PedidoResponseDTO)
def actualizar_pedido(
    pedido_id: int,
    pedido_data: PedidoUpdateDTO,
    db: Session = Depends(get_db)
):
    """Actualizar un pedido (solo en estados permitidos)"""
    pedido_service = PedidoService(db)
    return pedido_service.actualizar_pedido(pedido_id, pedido_data)

@router.post("/{pedido_id}/confirmar", response_model=PedidoResponseDTO)
async def confirmar_pedido(
    pedido_id: int,
    confirmacion_data: PedidoConfirmarDTO,
    db: Session = Depends(get_db)
):
    """Confirmar un pedido y ejecutar movimientos de stock"""
    pedido_service = PedidoService(db)
    return await pedido_service.confirmar_pedido(pedido_id, confirmacion_data)

@router.post("/{pedido_id}/cancelar", response_model=PedidoResponseDTO)
def cancelar_pedido(
    pedido_id: int,
    motivo: str = Query(..., description="Motivo de cancelación"),
    usuario: str = Header(..., alias="X-Usuario"),
    db: Session = Depends(get_db)
):
    """Cancelar un pedido"""
    pedido_service = PedidoService(db)
    return pedido_service.cancelar_pedido(pedido_id, motivo, usuario)

@router.get("/cliente/{cliente_id}", response_model=PedidoListResponseDTO)
def obtener_pedidos_cliente(
    cliente_id: int,
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(100, ge=1, le=1000, description="Tamaño de página"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db)
):
    """Obtener pedidos de un cliente específico"""
    pedido_service = PedidoService(db)
    return pedido_service.listar_pedidos(page, page_size, cliente_id, estado)

@router.get("/estado/{estado}", response_model=PedidoListResponseDTO)
def obtener_pedidos_por_estado(
    estado: str,
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(100, ge=1, le=1000, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    """Obtener pedidos por estado"""
    pedido_service = PedidoService(db)
    return pedido_service.listar_pedidos(page, page_size, None, estado)
