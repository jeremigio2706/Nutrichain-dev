"""
DTOs (Data Transfer Objects) para Almacén
Los DTOs definen la estructura de datos que se transfieren entre capas
"""

from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, validator

# ===== DTOs Base =====

class AlmacenBaseDTO(BaseModel):
    """DTO base para almacén"""
    nombre: str = Field(..., min_length=1, max_length=255, description="Nombre del almacén")
    codigo: str = Field(..., min_length=1, max_length=50, description="Código único del almacén")
    ubicacion: Optional[str] = Field(None, description="Dirección o ubicación del almacén")
    responsable: Optional[str] = Field(None, max_length=255, description="Responsable del almacén")
    telefono: Optional[str] = Field(None, max_length=50, description="Teléfono de contacto")
    email: Optional[str] = Field(None, max_length=255, description="Email de contacto")
    tipo: str = Field("general", max_length=50, description="Tipo de almacén")
    capacidad_maxima: Optional[Decimal] = Field(None, ge=0, description="Capacidad máxima")
    activo: bool = Field(True, description="Estado del almacén")
    
    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Email inválido')
        return v
    
    @validator('tipo')
    def validate_tipo(cls, v):
        tipos_validos = ["general", "frigorifco", "seco", "distribucion"]
        if v not in tipos_validos:
            raise ValueError(f'Tipo debe ser uno de: {tipos_validos}')
        return v

# ===== DTOs de Entrada =====

class AlmacenCreateDTO(AlmacenBaseDTO):
    """DTO para crear un almacén"""
    pass

class AlmacenUpdateDTO(BaseModel):
    """DTO para actualizar un almacén"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    codigo: Optional[str] = Field(None, min_length=1, max_length=50)
    ubicacion: Optional[str] = None
    responsable: Optional[str] = Field(None, max_length=255)
    telefono: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = None
    tipo: Optional[str] = Field(None, max_length=50)
    capacidad_maxima: Optional[Decimal] = Field(None, ge=0)
    activo: Optional[bool] = None
    
    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Email inválido')
        return v
    
    @validator('tipo')
    def validate_tipo(cls, v):
        if v is not None:
            tipos_validos = ["general", "frigorifco", "seco", "distribucion"]
            if v not in tipos_validos:
                raise ValueError(f'Tipo debe ser uno de: {tipos_validos}')
        return v

# ===== DTOs de Salida =====

class AlmacenResponseDTO(BaseModel):
    """DTO de respuesta para almacén"""
    id: int
    nombre: str
    codigo: str
    ubicacion: Optional[str]
    responsable: Optional[str]
    telefono: Optional[str]
    email: Optional[str]
    tipo: str
    capacidad_maxima: Optional[Decimal]
    activo: bool
    created_at: datetime
    updated_at: datetime
    
    # Campos calculados (opcionales)
    total_productos: Optional[int] = 0
    valor_inventario: Optional[Decimal] = Decimal('0.00')
    
    class Config:
        from_attributes = True

class AlmacenListDTO(BaseModel):
    """DTO para lista paginada de almacenes"""
    almacenes: List[AlmacenResponseDTO]
    total: int
    page: int = 1
    limit: Optional[int] = 20
    has_next: bool = False
    has_prev: bool = False

class AlmacenEstadisticasDTO(BaseModel):
    """DTO para estadísticas del almacén"""
    almacen_id: int
    almacen_nombre: str
    almacen_codigo: str
    total_productos: int
    total_stock: Decimal
    valor_inventario: Decimal
    productos_bajo_stock: int
    productos_sin_stock: int
    alertas_activas: int
    movimientos_mes: int
    ultimo_movimiento: Optional[datetime] = None

# ===== DTOs de Consulta =====

class AlmacenFiltrosDTO(BaseModel):
    """DTO para filtros de búsqueda de almacenes"""
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    tipo: Optional[str] = None
    responsable: Optional[str] = None
    activo: Optional[bool] = None
    skip: int = 0
    limit: int = 20
