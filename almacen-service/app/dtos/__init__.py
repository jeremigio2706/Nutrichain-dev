"""
DTOs (Data Transfer Objects) para el servicio de almacén
"""

# Importar todos los DTOs
from .almacen_dto import (
    AlmacenBaseDTO,
    AlmacenCreateDTO,
    AlmacenUpdateDTO,
    AlmacenResponseDTO,
    AlmacenListDTO,
    AlmacenEstadisticasDTO,
    AlmacenFiltrosDTO
)

from .stock_dto import (
    StockBaseDTO,
    StockCreateDTO,
    StockUpdateDTO,
    StockAjusteDTO,
    StockResponseDTO,
    StockResumenDTO,
    StockConsolidadoDTO,
    StockFiltrosDTO,
    StockDisponibilidadDTO,
    StockDisponibilidadResponseDTO,
    StockListDTO
)

from .movimiento_dto import (
    TipoMovimientoEnum,
    EstadoMovimientoEnum,
    MovimientoBaseDTO,
    MovimientoEntradaDTO,
    MovimientoSalidaDTO,
    MovimientoTransferenciaDTO,
    MovimientoAjusteDTO,
    MovimientoResponseDTO,
    MovimientoResumenDTO,
    MovimientoFiltrosDTO,
    MovimientoEstadisticasDTO,
    MovimientoListDTO,
    MovimientoHistorialDTO,
    StockActualizadoDTO,
    MovimientoConStockDTO
)

from .alerta_dto import (
    TipoAlertaEnum,
    NivelUrgenciaEnum,
    AlertaStockBaseDTO,
    AlertaStockCreateDTO,
    AlertaStockUpdateDTO,
    AlertaStockResolverDTO,
    AlertaStockResponseDTO,
    AlertaStockResumenDTO,
    AlertaStockFiltrosDTO,
    AlertaStockListDTO,
    AlertaStockDashboardDTO
)

__all__ = [
    # Almacén DTOs
    "AlmacenBaseDTO",
    "AlmacenCreateDTO",
    "AlmacenUpdateDTO",
    "AlmacenResponseDTO",
    "AlmacenListDTO",
    "AlmacenEstadisticasDTO",
    "AlmacenFiltrosDTO",
    
    # Stock DTOs
    "StockBaseDTO",
    "StockCreateDTO",
    "StockUpdateDTO",
    "StockAjusteDTO",
    "StockResponseDTO",
    "StockResumenDTO",
    "StockConsolidadoDTO",
    "StockFiltrosDTO",
    "StockDisponibilidadDTO",
    "StockDisponibilidadResponseDTO",
    "StockListDTO",
    
    # Movimiento DTOs
    "TipoMovimientoEnum",
    "EstadoMovimientoEnum",
    "MovimientoBaseDTO",
    "MovimientoEntradaDTO",
    "MovimientoSalidaDTO",
    "MovimientoTransferenciaDTO",
    "MovimientoAjusteDTO",
    "MovimientoResponseDTO",
    "MovimientoResumenDTO",
    "MovimientoFiltrosDTO",
    "MovimientoEstadisticasDTO",
    "MovimientoListDTO",
    "MovimientoHistorialDTO",
    
    # Alerta DTOs
    "TipoAlertaEnum",
    "NivelUrgenciaEnum",
    "AlertaStockBaseDTO",
    "AlertaStockCreateDTO",
    "AlertaStockUpdateDTO",
    "AlertaStockResolverDTO",
    "AlertaStockResponseDTO",
    "AlertaStockResumenDTO",
    "AlertaStockFiltrosDTO",
    "AlertaStockListDTO",
    "AlertaStockDashboardDTO"
]
