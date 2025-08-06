# ============================================================================
# devolucion_dto.py
#
# DTOs para operaciones relacionadas con devoluciones. Define estructuras
# para la gestión completa del proceso de devoluciones incluyendo motivos,
# estados y acciones con productos devueltos.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, validator

class DevolucionDetalleCreateDTO(BaseModel):
    """DTO para crear detalle de devolución"""
    producto_id: int = Field(..., gt=0, description="ID del producto")
    cantidad_devuelta: Decimal = Field(..., gt=0, description="Cantidad devuelta")
    motivo_detalle: Optional[str] = Field(None, max_length=100, description="Motivo específico del detalle")
    estado_producto: Optional[str] = Field(None, max_length=50, description="Estado del producto devuelto")
    accion: Optional[str] = Field(None, max_length=50, description="Acción a realizar")
    
    @validator('estado_producto')
    def validate_estado_producto(cls, v):
        if v is not None:
            estados_validos = ["bueno", "dañado", "vencido", "defectuoso"]
            if v not in estados_validos:
                raise ValueError(f'Estado del producto debe ser uno de: {estados_validos}')
        return v
    
    @validator('accion')
    def validate_accion(cls, v):
        if v is not None:
            acciones_validas = ["reintegrar_inventario", "descarte", "reparacion", "devolver_proveedor"]
            if v not in acciones_validas:
                raise ValueError(f'Acción debe ser una de: {acciones_validas}')
        return v

class DevolucionCreateDTO(BaseModel):
    """DTO para crear una devolución"""
    pedido_id: int = Field(..., gt=0, description="ID del pedido")
    envio_id: Optional[int] = Field(None, gt=0, description="ID del envío")
    motivo: str = Field(..., min_length=1, max_length=100, description="Motivo de la devolución")
    descripcion: Optional[str] = Field(None, description="Descripción detallada")
    detalles: List[DevolucionDetalleCreateDTO] = Field(..., min_items=1, description="Detalles de la devolución")

class DevolucionUpdateDTO(BaseModel):
    """DTO para actualizar una devolución"""
    motivo: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    estado: Optional[str] = Field(None, max_length=50)
    usuario_procesamiento: Optional[str] = Field(None, max_length=255)
    
    @validator('estado')
    def validate_estado(cls, v):
        if v is not None:
            estados_validos = ["recibida", "inspeccionada", "aprobada", "rechazada", "procesada"]
            if v not in estados_validos:
                raise ValueError(f'Estado debe ser uno de: {estados_validos}')
        return v

class DevolucionDetalleResponseDTO(BaseModel):
    """DTO de respuesta para detalle de devolución"""
    id: int
    producto_id: int
    cantidad_devuelta: Decimal
    motivo_detalle: Optional[str]
    estado_producto: Optional[str]
    accion: Optional[str]
    
    class Config:
        from_attributes = True

class DevolucionResponseDTO(BaseModel):
    """DTO de respuesta para devolución"""
    id: int
    numero_devolucion: str
    pedido_id: int
    envio_id: Optional[int]
    fecha_devolucion: datetime
    motivo: str
    descripcion: Optional[str]
    estado: str
    usuario_procesamiento: Optional[str]
    fecha_procesamiento: Optional[datetime]
    detalles: List[DevolucionDetalleResponseDTO]
    
    class Config:
        from_attributes = True

class DevolucionListResponseDTO(BaseModel):
    """DTO de respuesta para lista de devoluciones"""
    devoluciones: List[DevolucionResponseDTO]
    total: int
    page: int
    page_size: int
