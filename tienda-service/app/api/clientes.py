# ============================================================================
# clientes.py
#
# Endpoints API para gestión de clientes. Proporciona operaciones CRUD
# completas para clientes incluyendo búsqueda, validaciones y filtros
# de consulta.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.cliente_service import ClienteService
from ..dtos.cliente_dto import (
    ClienteCreateDTO, ClienteUpdateDTO, 
    ClienteResponseDTO, ClienteListResponseDTO
)

router = APIRouter()

@router.post("/", response_model=ClienteResponseDTO, status_code=201)
def crear_cliente(
    cliente_data: ClienteCreateDTO,
    db: Session = Depends(get_db)
):
    """Crear un nuevo cliente"""
    cliente_service = ClienteService(db)
    return cliente_service.crear_cliente(cliente_data)

@router.get("/{cliente_id}", response_model=ClienteResponseDTO)
def obtener_cliente(
    cliente_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un cliente por ID"""
    cliente_service = ClienteService(db)
    return cliente_service.obtener_cliente(cliente_id)

@router.get("/codigo/{codigo_cliente}", response_model=ClienteResponseDTO)
def obtener_cliente_por_codigo(
    codigo_cliente: str,
    db: Session = Depends(get_db)
):
    """Obtener un cliente por código"""
    cliente_service = ClienteService(db)
    return cliente_service.obtener_cliente_por_codigo(codigo_cliente)

@router.get("/", response_model=ClienteListResponseDTO)
def listar_clientes(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(100, ge=1, le=1000, description="Tamaño de página"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    db: Session = Depends(get_db)
):
    """Listar clientes con paginación"""
    cliente_service = ClienteService(db)
    return cliente_service.listar_clientes(page, page_size, activo)

@router.put("/{cliente_id}", response_model=ClienteResponseDTO)
def actualizar_cliente(
    cliente_id: int,
    cliente_data: ClienteUpdateDTO,
    db: Session = Depends(get_db)
):
    """Actualizar un cliente"""
    cliente_service = ClienteService(db)
    return cliente_service.actualizar_cliente(cliente_id, cliente_data)

@router.delete("/{cliente_id}")
def desactivar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db)
):
    """Desactivar un cliente"""
    cliente_service = ClienteService(db)
    cliente_service.desactivar_cliente(cliente_id)
    return {"message": "Cliente desactivado exitosamente"}

@router.get("/buscar/{term}", response_model=ClienteListResponseDTO)
def buscar_clientes(
    term: str,
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(100, ge=1, le=1000, description="Tamaño de página"),
    db: Session = Depends(get_db)
):
    """Buscar clientes por término"""
    cliente_service = ClienteService(db)
    return cliente_service.buscar_clientes(term, page, page_size)

@router.get("/{cliente_id}/validar-credito")
def validar_limite_credito(
    cliente_id: int,
    monto: float = Query(..., ge=0, description="Monto a validar"),
    db: Session = Depends(get_db)
):
    """Validar límite de crédito de un cliente"""
    cliente_service = ClienteService(db)
    es_valido = cliente_service.validar_limite_credito(cliente_id, monto)
    return {"cliente_id": cliente_id, "monto": monto, "credito_suficiente": es_valido}
