"""
API endpoints para gestión de almacenes
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.almacen_service import AlmacenService
from ..dtos.almacen_dto import (
    AlmacenCreateDTO,
    AlmacenUpdateDTO,
    AlmacenResponseDTO,
    AlmacenListDTO,
    AlmacenEstadisticasDTO,
    AlmacenFiltrosDTO
)

router = APIRouter(prefix="/almacenes", tags=["almacenes"])


@router.post("/", response_model=AlmacenResponseDTO, status_code=status.HTTP_201_CREATED)
def crear_almacen(
    almacen_data: AlmacenCreateDTO,
    db: Session = Depends(get_db)
):
    """Crear un nuevo almacén"""
    almacen_service = AlmacenService(db)
    return almacen_service.crear_almacen(almacen_data)


@router.get("/", response_model=AlmacenListDTO)
def listar_almacenes(
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo de almacén"),
    ubicacion: Optional[str] = Query(None, description="Filtrar por ubicación"),
    no_pagination: bool = Query(False, description="Si es true, devuelve todos los resultados sin paginación"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de resultados (ignorado si no_pagination=true)"),
    offset: int = Query(0, ge=0, description="Número de registros a saltar (ignorado si no_pagination=true)"),
    db: Session = Depends(get_db)
):
    """Listar almacenes con filtros opcionales y paginación configurable"""
    almacen_service = AlmacenService(db)
    # Si no_pagination es True, ignorar limit y offset
    final_limit = None if no_pagination else limit
    final_offset = 0 if no_pagination else offset
    
    return almacen_service.listar_almacenes(
        activo=activo,
        tipo=tipo,
        ubicacion=ubicacion,
        limit=final_limit,
        offset=final_offset
    )


@router.get("/{almacen_id}", response_model=AlmacenResponseDTO)
def obtener_almacen(
    almacen_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un almacén por su ID"""
    almacen_service = AlmacenService(db)
    return almacen_service.obtener_almacen(almacen_id)


@router.put("/{almacen_id}", response_model=AlmacenResponseDTO)
def actualizar_almacen(
    almacen_id: int,
    almacen_data: AlmacenUpdateDTO,
    db: Session = Depends(get_db)
):
    """Actualizar un almacén"""
    almacen_service = AlmacenService(db)
    return almacen_service.actualizar_almacen(almacen_id, almacen_data)


@router.delete("/{almacen_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_almacen(
    almacen_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar un almacén (soft delete)"""
    almacen_service = AlmacenService(db)
    return almacen_service.eliminar_almacen(almacen_id)


@router.get("/{almacen_id}/estadisticas", response_model=AlmacenEstadisticasDTO)
def obtener_estadisticas_almacen(
    almacen_id: int,
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de un almacén"""
    almacen_service = AlmacenService(db)
    return almacen_service.obtener_estadisticas(almacen_id)


@router.post("/{almacen_id}/activar", response_model=AlmacenResponseDTO)
def activar_almacen(
    almacen_id: int,
    db: Session = Depends(get_db)
):
    """Activar un almacén"""
    almacen_service = AlmacenService(db)
    almacen_data = AlmacenUpdateDTO(activo=True)
    return almacen_service.actualizar_almacen(almacen_id, almacen_data)


@router.post("/{almacen_id}/desactivar", response_model=AlmacenResponseDTO)
def desactivar_almacen(
    almacen_id: int,
    db: Session = Depends(get_db)
):
    """Desactivar un almacén"""
    almacen_service = AlmacenService(db)
    almacen_data = AlmacenUpdateDTO(activo=False)
    return almacen_service.actualizar_almacen(almacen_id, almacen_data)
