# ============================================================================
# cliente_dto.py
#
# DTOs para operaciones relacionadas con clientes. Define estructuras de
# datos para creación, actualización y respuesta de clientes, incluyendo
# validaciones de negocio y formateo de datos.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, validator

class ClienteBaseDTO(BaseModel):
    """DTO base para cliente"""
    codigo_cliente: str = Field(..., min_length=1, max_length=50, description="Código único del cliente")
    nombre: str = Field(..., min_length=1, max_length=255, description="Nombre del cliente")
    email: Optional[str] = Field(None, max_length=255, description="Email del cliente")
    telefono: Optional[str] = Field(None, max_length=50, description="Teléfono del cliente")
    direccion: Optional[str] = Field(None, description="Dirección del cliente")
    ciudad: Optional[str] = Field(None, max_length=100, description="Ciudad del cliente")
    pais: str = Field("Colombia", max_length=50, description="País del cliente")
    tipo_cliente: str = Field("minorista", max_length=50, description="Tipo de cliente")
    limite_credito: Decimal = Field(0, ge=0, description="Límite de crédito")
    descuento_porcentaje: Decimal = Field(0, ge=0, le=100, description="Porcentaje de descuento")
    activo: bool = Field(True, description="Estado del cliente")
    
    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Email inválido')
        return v
    
    @validator('tipo_cliente')
    def validate_tipo_cliente(cls, v):
        tipos_validos = ["minorista", "mayorista", "corporativo", "distribuidor"]
        if v not in tipos_validos:
            raise ValueError(f'Tipo debe ser uno de: {tipos_validos}')
        return v

class ClienteCreateDTO(ClienteBaseDTO):
    """DTO para crear un cliente"""
    pass

class ClienteUpdateDTO(BaseModel):
    """DTO para actualizar un cliente"""
    codigo_cliente: Optional[str] = Field(None, min_length=1, max_length=50)
    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    telefono: Optional[str] = Field(None, max_length=50)
    direccion: Optional[str] = None
    ciudad: Optional[str] = Field(None, max_length=100)
    pais: Optional[str] = Field(None, max_length=50)
    tipo_cliente: Optional[str] = Field(None, max_length=50)
    limite_credito: Optional[Decimal] = Field(None, ge=0)
    descuento_porcentaje: Optional[Decimal] = Field(None, ge=0, le=100)
    activo: Optional[bool] = None

class ClienteResponseDTO(BaseModel):
    """DTO de respuesta para cliente"""
    id: int
    codigo_cliente: str
    nombre: str
    email: Optional[str]
    telefono: Optional[str]
    direccion: Optional[str]
    ciudad: Optional[str]
    pais: str
    tipo_cliente: str
    limite_credito: Decimal
    descuento_porcentaje: Decimal
    activo: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ClienteListResponseDTO(BaseModel):
    """DTO de respuesta para lista de clientes"""
    clientes: List[ClienteResponseDTO]
    total: int
    page: int
    page_size: int
