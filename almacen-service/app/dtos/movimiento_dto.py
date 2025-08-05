"""
DTOs (Data Transfer Objects) para Movimientos
"""

from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

# ===== Enums =====

class TipoMovimientoEnum(str, Enum):
    """Enum para tipos de movimiento"""
    ENTRADA = "entrada"
    SALIDA = "salida"
    TRANSFERENCIA = "transferencia"
    AJUSTE = "ajuste"
    DEVOLUCION = "devolucion"

class EstadoMovimientoEnum(str, Enum):
    """Enum para estados de movimiento"""
    PENDIENTE = "pendiente"
    PROCESADO = "procesado"
    CANCELADO = "cancelado"

# ===== DTOs Base =====

class MovimientoBaseDTO(BaseModel):
    """DTO base para movimiento"""
    producto_id: int = Field(..., gt=0, description="ID del producto")
    tipo_movimiento: TipoMovimientoEnum = Field(..., description="Tipo de movimiento")
    cantidad: Decimal = Field(..., gt=0, description="Cantidad del movimiento")
    motivo: Optional[str] = Field(None, description="Motivo del movimiento")
    referencia_externa: Optional[str] = Field(None, max_length=255, description="Referencia externa")
    costo_unitario: Optional[Decimal] = Field(None, ge=0, description="Costo unitario")
    usuario: Optional[str] = Field(None, max_length=255, description="Usuario que registra")
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales")

# ===== DTOs de Entrada =====

class MovimientoEntradaDTO(MovimientoBaseDTO):
    """DTO para movimiento de entrada"""
    almacen_destino_id: int = Field(..., gt=0, description="ID del almacén destino")
    
    @validator('tipo_movimiento')
    def validate_tipo_entrada(cls, v):
        tipos_validos = [TipoMovimientoEnum.ENTRADA, TipoMovimientoEnum.DEVOLUCION]
        if v not in tipos_validos:
            raise ValueError(f'Para entrada debe ser: {[t.value for t in tipos_validos]}')
        return v

class MovimientoSalidaDTO(MovimientoBaseDTO):
    """DTO para movimiento de salida"""
    almacen_origen_id: int = Field(..., gt=0, description="ID del almacén origen")
    
    @validator('tipo_movimiento')
    def validate_tipo_salida(cls, v):
        tipos_validos = [TipoMovimientoEnum.SALIDA, TipoMovimientoEnum.AJUSTE]
        if v not in tipos_validos:
            raise ValueError(f'Para salida debe ser: {[t.value for t in tipos_validos]}')
        return v

class MovimientoTransferenciaDTO(MovimientoBaseDTO):
    """DTO para movimiento de transferencia"""
    almacen_origen_id: int = Field(..., gt=0, description="ID del almacén origen")
    almacen_destino_id: int = Field(..., gt=0, description="ID del almacén destino")
    
    @validator('tipo_movimiento')
    def validate_tipo_transferencia(cls, v):
        if v != TipoMovimientoEnum.TRANSFERENCIA:
            raise ValueError('Para transferencia el tipo debe ser "transferencia"')
        return v
    
    @validator('almacen_destino_id')
    def validate_almacenes_diferentes(cls, v, values):
        if 'almacen_origen_id' in values and v == values['almacen_origen_id']:
            raise ValueError('Los almacenes de origen y destino deben ser diferentes')
        return v

class MovimientoAjusteDTO(BaseModel):
    """DTO para movimiento de ajuste de inventario"""
    producto_id: int = Field(..., gt=0, description="ID del producto")
    almacen_id: int = Field(..., gt=0, description="ID del almacén")
    nueva_cantidad: Decimal = Field(..., ge=0, description="Nueva cantidad después del ajuste")
    motivo: str = Field(..., max_length=255, description="Motivo del ajuste")
    usuario: Optional[str] = Field(None, max_length=255, description="Usuario que realiza el ajuste")
    observaciones: Optional[str] = Field(None, description="Observaciones del ajuste")

class MovimientoAjusteInicialDTO(MovimientoBaseDTO):
    """
    DTO para movimiento de ajuste inicial (ÚNICA forma segura de crear stock inicial)
    
    NIVEL SENIOR: Este es el reemplazo para crear stock directamente.
    Todo stock inicial debe tener un movimiento de ajuste que lo justifique.
    """
    almacen_id: int = Field(..., gt=0, description="ID del almacén donde se crea el stock inicial")
    cantidad_inicial: Decimal = Field(..., ge=0, description="Cantidad inicial del stock")
    cantidad_minima: Optional[Decimal] = Field(None, ge=0, description="Cantidad mínima recomendada")
    cantidad_maxima: Optional[Decimal] = Field(None, ge=0, description="Cantidad máxima recomendada")
    costo_unitario: Optional[Decimal] = Field(None, ge=0, description="Costo unitario del producto")
    
    @validator('tipo_movimiento')
    def validate_tipo_ajuste_inicial(cls, v):
        if v != TipoMovimientoEnum.AJUSTE:
            raise ValueError('Para ajuste inicial el tipo debe ser "ajuste"')
        return v

# ===== DTOs de Salida =====

class MovimientoResponseDTO(BaseModel):
    """DTO de respuesta para movimiento"""
    id: int
    producto_id: int
    almacen_origen_id: Optional[int]
    almacen_destino_id: Optional[int]
    tipo_movimiento: str
    cantidad: Decimal
    cantidad_real: Optional[Decimal]
    motivo: Optional[str]
    referencia_externa: Optional[str]
    costo_unitario: Optional[Decimal]
    costo_total: Optional[Decimal]
    fecha_movimiento: datetime
    fecha_procesamiento: Optional[datetime]
    usuario: Optional[str]
    estado: str
    observaciones: Optional[str]
    
    # Campos adicionales (calculados)
    almacen_origen_nombre: Optional[str] = None
    almacen_destino_nombre: Optional[str] = None
    
    class Config:
        from_attributes = True

class MovimientoResumenDTO(BaseModel):
    """DTO para resumen de movimiento"""
    fecha: datetime
    tipo_movimiento: str
    producto_id: int
    cantidad: Decimal
    almacen_origen: Optional[str]
    almacen_destino: Optional[str]
    usuario: Optional[str]
    estado: str

# ===== DTOs de Consulta =====

class MovimientoFiltrosDTO(BaseModel):
    """DTO para filtros de búsqueda de movimientos"""
    producto_id: Optional[int] = None
    almacen_id: Optional[int] = None  # Busca en origen O destino
    almacen_origen_id: Optional[int] = None
    almacen_destino_id: Optional[int] = None
    tipo_movimiento: Optional[TipoMovimientoEnum] = None
    estado: Optional[EstadoMovimientoEnum] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    usuario: Optional[str] = None
    referencia_externa: Optional[str] = None
    skip: int = 0
    limit: int = 100

class MovimientoEstadisticasDTO(BaseModel):
    """DTO para estadísticas de movimientos"""
    periodo_desde: datetime
    periodo_hasta: datetime
    total_movimientos: int
    movimientos_por_tipo: dict  # {tipo: cantidad}
    movimientos_por_estado: dict  # {estado: cantidad}
    valor_total_movido: Decimal
    productos_mas_movidos: List[dict]  # {producto_id, cantidad_total}
    almacenes_mas_activos: List[dict]  # {almacen_id, cantidad_movimientos}

# ===== DTOs de Lista =====

class MovimientoListDTO(BaseModel):
    """DTO para lista paginada de movimientos"""
    movimientos: List[MovimientoResponseDTO]
    total: int
    page: int = 1
    limit: Optional[int] = 100
    has_next: bool = False
    has_prev: bool = False

class MovimientoHistorialDTO(BaseModel):
    """DTO para historial de movimientos de un producto/almacén"""
    movimientos: List[MovimientoResumenDTO]
    resumen: dict  # Estadísticas del historial
    total: int

# ===== DTOs de Respuesta Combinada =====

class StockActualizadoDTO(BaseModel):
    """DTO para información de stock después de un movimiento"""
    stock_id: int
    producto_id: int
    almacen_id: int
    cantidad_actual: Decimal
    cantidad_disponible: Decimal
    fecha_actualizacion: datetime

class MovimientoConStockDTO(BaseModel):
    """DTO para respuesta combinada de movimiento y stock actualizado"""
    movimiento: MovimientoResponseDTO
    stock_actualizado: Optional[StockActualizadoDTO]
