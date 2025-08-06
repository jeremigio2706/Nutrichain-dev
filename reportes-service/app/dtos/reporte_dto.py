# ============================================================================
# reporte_dto.py
#
# DTOs para operaciones de reportes y consolidación de datos. Define
# estructuras para reportes de stock valorizado, pedidos por cliente,
# trazabilidad de productos y análisis de ventas.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, date
from pydantic import BaseModel, Field

class StockValorizadoItemDTO(BaseModel):
    """DTO para item de stock valorizado"""
    producto_id: int
    sku: str
    nombre_producto: str
    categoria: Optional[str]
    almacen_id: int
    almacen_nombre: str
    cantidad_actual: Decimal
    costo_unitario: Optional[Decimal]
    valor_total: Optional[Decimal]
    estado_stock: str
    ultima_actualizacion: datetime

class StockValorizadoResponseDTO(BaseModel):
    """DTO de respuesta para reporte de stock valorizado"""
    items: List[StockValorizadoItemDTO]
    resumen: Dict[str, Any]
    fecha_reporte: datetime
    total_productos: int
    valor_total_inventario: Decimal

class PedidoClienteItemDTO(BaseModel):
    """DTO para item de pedido en reporte de cliente"""
    producto_id: int
    sku: str
    nombre_producto: str
    cantidad: Decimal
    precio_unitario: Decimal
    subtotal: Decimal

class PedidoClienteDTO(BaseModel):
    """DTO para pedido en reporte de cliente"""
    pedido_id: int
    numero_pedido: str
    fecha_pedido: datetime
    estado: str
    total: Decimal
    items: List[PedidoClienteItemDTO]

class PedidosClienteResponseDTO(BaseModel):
    """DTO de respuesta para reporte de pedidos por cliente"""
    cliente_id: int
    nombre_cliente: str
    email_cliente: str
    pedidos: List[PedidoClienteDTO]
    resumen: Dict[str, Any]
    fecha_inicio: Optional[date]
    fecha_fin: Optional[date]
    total_pedidos: int
    valor_total: Decimal

class MovimientoTrazabilidadDTO(BaseModel):
    """DTO para movimiento en trazabilidad"""
    id: int
    tipo_movimiento: str
    cantidad: Decimal
    motivo: str
    almacen_origen: Optional[str]
    almacen_destino: Optional[str]
    fecha_movimiento: datetime
    usuario: str
    referencia_externa: Optional[str]

class PedidoTrazabilidadDTO(BaseModel):
    """DTO para pedido en trazabilidad"""
    pedido_id: int
    numero_pedido: str
    cliente_nombre: str
    cantidad: Decimal
    precio_unitario: Decimal
    fecha_pedido: datetime
    estado: str

class TrazabilidadProductoResponseDTO(BaseModel):
    """DTO de respuesta para trazabilidad de producto"""
    producto_id: int
    sku: str
    nombre_producto: str
    categoria: Optional[str]
    movimientos: List[MovimientoTrazabilidadDTO]
    pedidos: List[PedidoTrazabilidadDTO]
    resumen: Dict[str, Any]
    fecha_inicio: Optional[date]
    fecha_fin: Optional[date]

class VentasResumenDTO(BaseModel):
    """DTO para resumen de ventas"""
    fecha: date
    total_pedidos: int
    total_productos_vendidos: Decimal
    valor_total_ventas: Decimal
    productos_mas_vendidos: List[Dict[str, Any]]

class VentasReporteResponseDTO(BaseModel):
    """DTO de respuesta para reporte de ventas"""
    ventas_por_dia: List[VentasResumenDTO]
    resumen_periodo: Dict[str, Any]
    fecha_inicio: date
    fecha_fin: date
    total_general: Decimal

class ReporteParametrosDTO(BaseModel):
    """DTO para parámetros de reportes"""
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    cliente_id: Optional[int] = None
    producto_id: Optional[int] = None
    almacen_id: Optional[int] = None
    estado: Optional[str] = None
    limit: Optional[int] = Field(100, ge=1, le=1000)
    offset: Optional[int] = Field(0, ge=0)
