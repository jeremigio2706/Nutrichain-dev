"""
DTOs (Data Transfer Objects) para Alertas de Stock
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

# ===== Enums =====

class TipoAlertaEnum(str, Enum):
    """Enum para tipos de alerta"""
    STOCK_BAJO = "stock_bajo"
    STOCK_AGOTADO = "stock_agotado"
    SOBRECARGA = "sobrecarga"
    VENCIMIENTO_PROXIMO = "vencimiento_proximo"

class NivelUrgenciaEnum(str, Enum):
    """Enum para niveles de urgencia"""
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"

# ===== DTOs Base =====

class AlertaStockBaseDTO(BaseModel):
    """DTO base para alerta de stock"""
    producto_id: int = Field(..., gt=0, description="ID del producto")
    almacen_id: int = Field(..., gt=0, description="ID del almacén")
    tipo_alerta: TipoAlertaEnum = Field(..., description="Tipo de alerta")
    descripcion: Optional[str] = Field(None, description="Descripción de la alerta")
    nivel_urgencia: NivelUrgenciaEnum = Field(NivelUrgenciaEnum.MEDIO, description="Nivel de urgencia")

# ===== DTOs de Entrada =====

class AlertaStockCreateDTO(AlertaStockBaseDTO):
    """DTO para crear alerta de stock"""
    pass

class AlertaStockUpdateDTO(BaseModel):
    """DTO para actualizar alerta de stock"""
    descripcion: Optional[str] = None
    nivel_urgencia: Optional[NivelUrgenciaEnum] = None
    leida: Optional[bool] = None

class AlertaStockResolverDTO(BaseModel):
    """DTO para resolver alerta de stock"""
    observaciones: Optional[str] = Field(None, description="Observaciones de resolución")
    usuario_resolucion: Optional[str] = Field(None, max_length=255, description="Usuario que resuelve")

# ===== DTOs de Salida =====

class AlertaStockResponseDTO(BaseModel):
    """DTO de respuesta para alerta de stock"""
    id: int
    producto_id: int
    almacen_id: int
    tipo_alerta: str
    descripcion: Optional[str]
    nivel_urgencia: str
    leida: bool
    fecha_alerta: datetime
    fecha_resolucion: Optional[datetime]
    
    # Campos adicionales (calculados)
    almacen_nombre: Optional[str] = None
    tiempo_transcurrido: Optional[str] = None  # "2 días", "3 horas", etc.
    esta_activa: bool = True
    
    class Config:
        from_attributes = True

class AlertaStockResumenDTO(BaseModel):
    """DTO para resumen de alertas"""
    total_alertas: int
    alertas_por_tipo: dict  # {tipo: cantidad}
    alertas_por_urgencia: dict  # {urgencia: cantidad}
    alertas_no_leidas: int
    alertas_activas: int
    alertas_resueltas_hoy: int

# ===== DTOs de Consulta =====

class AlertaStockFiltrosDTO(BaseModel):
    """DTO para filtros de búsqueda de alertas"""
    producto_id: Optional[int] = None
    almacen_id: Optional[int] = None
    tipo_alerta: Optional[TipoAlertaEnum] = None
    nivel_urgencia: Optional[NivelUrgenciaEnum] = None
    leida: Optional[bool] = None
    activa: Optional[bool] = None  # True para alertas sin resolver
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    skip: int = 0
    limit: int = 100

# ===== DTOs de Lista =====

class AlertaStockListDTO(BaseModel):
    """DTO para lista paginada de alertas"""
    alertas: List[AlertaStockResponseDTO]
    total: int
    page: int = 1
    limit: int = 100
    has_next: bool = False
    has_prev: bool = False

class AlertaStockDashboardDTO(BaseModel):
    """DTO para dashboard de alertas"""
    alertas_criticas: List[AlertaStockResponseDTO]
    alertas_altas: List[AlertaStockResponseDTO]
    resumen: AlertaStockResumenDTO
    tendencias: dict  # Tendencias de alertas por día/semana
