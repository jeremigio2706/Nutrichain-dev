# ============================================================================
# pedido_dto.py
#
# DTOs para operaciones relacionadas con pedidos. Define estructuras para
# creación, actualización y consulta de pedidos incluyendo validaciones
# de negocio y gestión de estados del ciclo de vida del pedido.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from typing import Optional, List
from decimal import Decimal
from datetime import datetime, date
from pydantic import BaseModel, Field, validator

class PedidoDetalleCreateDTO(BaseModel):
    """DTO para crear detalle de pedido"""
    producto_id: int = Field(..., gt=0, description="ID del producto")
    cantidad: Decimal = Field(..., gt=0, description="Cantidad del producto")
    precio_unitario: Decimal = Field(..., gt=0, description="Precio unitario")
    descuento_linea: Decimal = Field(0, ge=0, description="Descuento por línea")
    almacen_origen_id: Optional[int] = Field(None, gt=0, description="ID del almacén origen")

class PedidoCreateDTO(BaseModel):
    """DTO para crear un pedido"""
    cliente_id: int = Field(..., gt=0, description="ID del cliente")
    fecha_requerida: Optional[date] = Field(None, description="Fecha requerida de entrega")
    fecha_prometida: Optional[date] = Field(None, description="Fecha prometida de entrega")
    metodo_pago: Optional[str] = Field(None, max_length=50, description="Método de pago")
    almacen_origen_id: Optional[int] = Field(None, gt=0, description="ID del almacén origen")
    direccion_entrega: Optional[str] = Field(None, description="Dirección de entrega")
    observaciones: Optional[str] = Field(None, description="Observaciones del pedido")
    prioridad: str = Field("normal", max_length=20, description="Prioridad del pedido")
    detalles: List[PedidoDetalleCreateDTO] = Field(..., min_items=1, description="Detalles del pedido")
    
    @validator('prioridad')
    def validate_prioridad(cls, v):
        prioridades_validas = ["baja", "normal", "alta", "urgente"]
        if v not in prioridades_validas:
            raise ValueError(f'Prioridad debe ser una de: {prioridades_validas}')
        return v

class PedidoUpdateDTO(BaseModel):
    """DTO para actualizar un pedido"""
    fecha_requerida: Optional[date] = None
    fecha_prometida: Optional[date] = None
    estado: Optional[str] = Field(None, max_length=50)
    metodo_pago: Optional[str] = Field(None, max_length=50)
    direccion_entrega: Optional[str] = None
    observaciones: Optional[str] = None
    prioridad: Optional[str] = Field(None, max_length=20)
    usuario_aprobacion: Optional[str] = Field(None, max_length=255)
    motivo_cancelacion: Optional[str] = None

class PedidoConfirmarDTO(BaseModel):
    """DTO para confirmar un pedido"""
    usuario_aprobacion: str = Field(..., min_length=1, max_length=255, description="Usuario que aprueba")
    observaciones: Optional[str] = Field(None, description="Observaciones de la confirmación")

class PedidoDetalleResponseDTO(BaseModel):
    """DTO de respuesta para detalle de pedido"""
    id: int
    producto_id: int
    cantidad: Decimal
    precio_unitario: Decimal
    descuento_linea: Decimal
    subtotal_linea: Decimal
    
    class Config:
        from_attributes = True

class PedidoResponseDTO(BaseModel):
    """DTO de respuesta para pedido"""
    id: int
    numero_pedido: str
    cliente_id: int
    fecha_pedido: datetime
    fecha_requerida: Optional[date]
    fecha_prometida: Optional[date]
    fecha_entrega: Optional[datetime]
    estado: str
    subtotal: Decimal
    descuento: Decimal
    impuestos: Decimal
    total: Decimal
    metodo_pago: Optional[str]
    almacen_origen_id: Optional[int]
    direccion_entrega: Optional[str]
    observaciones: Optional[str]
    prioridad: str
    usuario_creacion: Optional[str]
    usuario_aprobacion: Optional[str]
    fecha_aprobacion: Optional[datetime]
    motivo_cancelacion: Optional[str]
    detalles: List[PedidoDetalleResponseDTO]
    
    class Config:
        from_attributes = True

class PedidoListResponseDTO(BaseModel):
    """DTO de respuesta para lista de pedidos"""
    pedidos: List[PedidoResponseDTO]
    total: int
    page: int
    page_size: int

class ConsultarDisponibilidadDTO(BaseModel):
    """DTO para consultar disponibilidad de productos"""
    productos: List[dict] = Field(..., description="Lista de productos con producto_id, cantidad y almacen_id")

class ReservaStockDTO(BaseModel):
    """DTO para reserva de stock"""
    pedido_id: int
    producto_id: int
    cantidad_reservada: Decimal
    almacen_id: int
