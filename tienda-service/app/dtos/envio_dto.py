# ============================================================================
# envio_dto.py
#
# DTOs para operaciones relacionadas con envíos. Define estructuras para
# la gestión de logística de entregas incluyendo transportistas, vehículos
# y seguimiento de estados de envío.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, validator

class EnvioCreateDTO(BaseModel):
    """DTO para crear un envío"""
    pedido_id: int = Field(..., gt=0, description="ID del pedido")
    transportista: Optional[str] = Field(None, max_length=255, description="Nombre del transportista")
    vehiculo: Optional[str] = Field(None, max_length=100, description="Vehículo asignado")
    conductor: Optional[str] = Field(None, max_length=255, description="Nombre del conductor")
    telefono_conductor: Optional[str] = Field(None, max_length=50, description="Teléfono del conductor")
    fecha_programada: Optional[datetime] = Field(None, description="Fecha programada de envío")
    observaciones: Optional[str] = Field(None, description="Observaciones del envío")
    costo_envio: Optional[Decimal] = Field(None, ge=0, description="Costo del envío")

class EnvioUpdateDTO(BaseModel):
    """DTO para actualizar un envío"""
    transportista: Optional[str] = Field(None, max_length=255)
    vehiculo: Optional[str] = Field(None, max_length=100)
    conductor: Optional[str] = Field(None, max_length=255)
    telefono_conductor: Optional[str] = Field(None, max_length=50)
    fecha_programada: Optional[datetime] = None
    fecha_salida: Optional[datetime] = None
    fecha_entrega: Optional[datetime] = None
    estado: Optional[str] = Field(None, max_length=50)
    observaciones: Optional[str] = None
    costo_envio: Optional[Decimal] = Field(None, ge=0)
    
    @validator('estado')
    def validate_estado(cls, v):
        if v is not None:
            estados_validos = ["programado", "en_transito", "entregado", "devuelto", "cancelado"]
            if v not in estados_validos:
                raise ValueError(f'Estado debe ser uno de: {estados_validos}')
        return v

class EnvioResponseDTO(BaseModel):
    """DTO de respuesta para envío"""
    id: int
    numero_envio: str
    pedido_id: int
    transportista: Optional[str]
    vehiculo: Optional[str]
    conductor: Optional[str]
    telefono_conductor: Optional[str]
    fecha_programada: Optional[datetime]
    fecha_salida: Optional[datetime]
    fecha_entrega: Optional[datetime]
    estado: str
    observaciones: Optional[str]
    costo_envio: Optional[Decimal]
    
    class Config:
        from_attributes = True

class EnvioListResponseDTO(BaseModel):
    """DTO de respuesta para lista de envíos"""
    envios: List[EnvioResponseDTO]
    total: int
    page: int
    page_size: int
