"""
DTOs (Data Transfer Objects) para Stock
"""

from typing import Optional, List
from decimal import Decimal
from datetime import datetime, date
from pydantic import BaseModel, Field, validator

# ===== DTOs Base =====

class StockBaseDTO(BaseModel):
    """DTO base para stock"""
    producto_id: int = Field(..., gt=0, description="ID del producto")
    almacen_id: int = Field(..., gt=0, description="ID del almacén")
    cantidad_actual: Decimal = Field(..., ge=0, description="Cantidad actual en stock")
    cantidad_reservada: Decimal = Field(0, ge=0, description="Cantidad reservada")
    cantidad_minima: Optional[Decimal] = Field(None, ge=0, description="Cantidad mínima para alerta")
    cantidad_maxima: Optional[Decimal] = Field(None, gt=0, description="Cantidad máxima permitida")
    ubicacion_fisica: Optional[str] = Field(None, max_length=255, description="Ubicación física en almacén")
    lote: Optional[str] = Field(None, max_length=100, description="Número de lote")
    fecha_vencimiento: Optional[date] = Field(None, description="Fecha de vencimiento")
    costo_unitario: Optional[Decimal] = Field(None, ge=0, description="Costo unitario")
    
    @validator('cantidad_maxima')
    def validate_cantidad_maxima(cls, v, values):
        if v is not None and 'cantidad_minima' in values and values['cantidad_minima'] is not None:
            if v <= values['cantidad_minima']:
                raise ValueError('Cantidad máxima debe ser mayor a la mínima')
        return v

# ===== DTOs de Entrada =====

class StockCreateDTO(StockBaseDTO):
    """DTO para crear stock"""
    pass

class StockUpdateDTO(BaseModel):
    """DTO para actualizar stock"""
    cantidad_actual: Optional[Decimal] = Field(None, ge=0)
    cantidad_reservada: Optional[Decimal] = Field(None, ge=0)
    cantidad_minima: Optional[Decimal] = Field(None, ge=0)
    cantidad_maxima: Optional[Decimal] = Field(None, gt=0)
    ubicacion_fisica: Optional[str] = Field(None, max_length=255)
    lote: Optional[str] = Field(None, max_length=100)
    fecha_vencimiento: Optional[date] = None
    costo_unitario: Optional[Decimal] = Field(None, ge=0)

class StockAjusteDTO(BaseModel):
    """DTO para ajuste de stock"""
    nueva_cantidad: Decimal = Field(..., ge=0, description="Nueva cantidad")
    motivo: str = Field(..., max_length=255, description="Motivo del ajuste")
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales")
    usuario: Optional[str] = Field(None, max_length=255, description="Usuario que realiza el ajuste")

# ===== DTOs de Salida =====

class StockResponseDTO(BaseModel):
    """DTO de respuesta para stock"""
    id: int
    producto_id: int
    almacen_id: int
    cantidad_actual: Decimal
    cantidad_reservada: Decimal
    cantidad_disponible: Decimal  # Calculado: actual - reservada
    cantidad_minima: Optional[Decimal]
    cantidad_maxima: Optional[Decimal]
    ubicacion_fisica: Optional[str]
    lote: Optional[str]
    fecha_vencimiento: Optional[date]
    costo_unitario: Optional[Decimal]
    updated_at: datetime
    
    # Campos adicionales (calculados)
    estado_stock: str  # disponible, bajo_stock, sin_stock, sobrecarga
    dias_para_vencimiento: Optional[int] = None
    valor_total: Optional[Decimal] = None
    
    class Config:
        from_attributes = True

class StockResumenDTO(BaseModel):
    """DTO para resumen de stock"""
    producto_id: int
    almacen_id: int
    almacen_nombre: str
    cantidad_actual: Decimal
    cantidad_disponible: Decimal
    cantidad_minima: Optional[Decimal]
    estado_stock: str
    valor_total: Optional[Decimal]
    requiere_atencion: bool  # True si necesita reposición o tiene alertas

class StockConsolidadoDTO(BaseModel):
    """DTO para stock consolidado por producto (todos los almacenes)"""
    producto_id: int
    cantidad_total: Decimal
    cantidad_disponible_total: Decimal
    almacenes_con_stock: int
    almacenes_sin_stock: int
    valor_total: Decimal
    detalle_almacenes: List[StockResumenDTO]

# ===== DTOs de Consulta =====

class StockFiltrosDTO(BaseModel):
    """DTO para filtros de búsqueda de stock"""
    producto_id: Optional[int] = None
    almacen_id: Optional[int] = None
    cantidad_minima_desde: Optional[Decimal] = None
    cantidad_minima_hasta: Optional[Decimal] = None
    solo_bajo_stock: bool = False
    solo_sin_stock: bool = False
    solo_con_stock: bool = False
    lote: Optional[str] = None
    fecha_vencimiento_hasta: Optional[date] = None
    ubicacion_fisica: Optional[str] = None
    skip: int = 0
    limit: int = 100

class StockDisponibilidadDTO(BaseModel):
    """DTO para consulta de disponibilidad"""
    producto_id: int = Field(..., gt=0, description="ID del producto")
    cantidad_requerida: Decimal = Field(..., gt=0, description="Cantidad requerida")
    almacen_id: Optional[int] = Field(None, description="ID del almacén específico (opcional)")

class StockDisponibilidadResponseDTO(BaseModel):
    """DTO de respuesta para disponibilidad"""
    producto_id: int
    cantidad_requerida: Decimal
    cantidad_disponible_total: Decimal
    disponible: bool
    almacenes_disponibles: List[dict]  # {almacen_id, almacen_nombre, cantidad_disponible, puede_cubrir}
    sugerencias: List[str]  # Sugerencias para obtener el stock

# ===== DTOs de Lista =====

class StockListDTO(BaseModel):
    """DTO para lista paginada de stock"""
    items: List[StockResponseDTO]  # Cambiado de stocks a items
    total: int
    page: int = 1
    limit: Optional[int] = 100
    has_next: bool = False
    has_prev: bool = False
