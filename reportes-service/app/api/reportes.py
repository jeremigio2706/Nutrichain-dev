# ============================================================================
# reportes.py
#
# Endpoints de la API para el servicio de reportes. Proporciona endpoints
# para generar reportes de stock valorizado, pedidos por cliente y
# trazabilidad de productos.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, Path
from fastapi.responses import JSONResponse

from ..services.reporte_service import ReporteService
from ..dtos.reporte_dto import (
    StockValorizadoResponseDTO, PedidosClienteResponseDTO, 
    TrazabilidadProductoResponseDTO
)
from ..exceptions.api_exceptions import (
    ParametrosInvalidosError, DatosInsuficientesError
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/reportes", tags=["Reportes"])

def get_reporte_service() -> ReporteService:
    """Dependency para obtener instancia del servicio de reportes"""
    return ReporteService()

@router.get(
    "/stock-valorizado",
    response_model=StockValorizadoResponseDTO,
    summary="Reporte de Stock Valorizado",
    description="Genera un reporte consolidado del stock valorizado por almacén",
    responses={
        200: {"description": "Reporte generado exitosamente"},
        400: {"description": "Parámetros inválidos"},
        404: {"description": "No hay datos suficientes"},
        503: {"description": "Servicio externo no disponible"}
    }
)
async def get_stock_valorizado(
    almacen_id: Optional[int] = Query(None, description="ID del almacén (opcional, para todos si no se especifica)"),
    incluir_sin_stock: bool = Query(False, description="Incluir productos sin stock"),
    categoria_id: Optional[int] = Query(None, description="Filtrar por categoría de producto"),
    reporte_service: ReporteService = Depends(get_reporte_service)
):
    """
    Genera un reporte de stock valorizado consolidando datos de
    almacén y catálogo
    """
    logger.info(f"Generando reporte stock valorizado - almacen_id: {almacen_id}")
    
    try:
        resultado = await reporte_service.generar_stock_valorizado(
            almacen_id=almacen_id,
            incluir_sin_stock=incluir_sin_stock,
            categoria_id=categoria_id
        )
        
        logger.info(f"Reporte stock valorizado generado - {len(resultado.items)} productos")
        return resultado
        
    except Exception as e:
        logger.error(f"Error generando stock valorizado: {str(e)}")
        raise

@router.get(
    "/pedidos-cliente/{cliente_id}",
    response_model=PedidosClienteResponseDTO,
    summary="Reporte de Pedidos por Cliente",
    description="Genera un reporte histórico de pedidos de un cliente específico",
    responses={
        200: {"description": "Reporte generado exitosamente"},
        400: {"description": "Parámetros inválidos"},
        404: {"description": "Cliente no encontrado o sin pedidos"},
        503: {"description": "Servicio externo no disponible"}
    }
)
async def get_pedidos_cliente(
    cliente_id: int = Path(..., description="ID del cliente"),
    fecha_desde: Optional[datetime] = Query(None, description="Fecha inicio del período (ISO format)"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha fin del período (ISO format)"),
    estado: Optional[str] = Query(None, description="Filtrar por estado del pedido"),
    incluir_detalles: bool = Query(True, description="Incluir detalles de productos"),
    reporte_service: ReporteService = Depends(get_reporte_service)
):
    """
    Genera un reporte histórico de pedidos para un cliente específico
    consolidando datos de tienda y catálogo
    """
    logger.info(f"Generando reporte pedidos cliente - cliente_id: {cliente_id}")
    
    # Validar parámetros de fecha
    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        raise ParametrosInvalidosError("La fecha desde debe ser anterior a fecha hasta")
    
    try:
        resultado = await reporte_service.generar_pedidos_cliente(
            cliente_id=cliente_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            estado=estado,
            incluir_detalles=incluir_detalles
        )
        
        logger.info(f"Reporte pedidos cliente generado - {len(resultado.pedidos)} pedidos")
        return resultado
        
    except Exception as e:
        logger.error(f"Error generando pedidos cliente: {str(e)}")
        raise

@router.get(
    "/trazabilidad-producto/{producto_id}",
    response_model=TrazabilidadProductoResponseDTO,
    summary="Trazabilidad de Producto",
    description="Genera un reporte de trazabilidad completa de un producto",
    responses={
        200: {"description": "Reporte generado exitosamente"},
        400: {"description": "Parámetros inválidos"},
        404: {"description": "Producto no encontrado"},
        503: {"description": "Servicio externo no disponible"}
    }
)
async def get_trazabilidad_producto(
    producto_id: int = Path(..., description="ID del producto"),
    fecha_desde: Optional[datetime] = Query(None, description="Fecha inicio del período (ISO format)"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha fin del período (ISO format)"),
    incluir_movimientos: bool = Query(True, description="Incluir movimientos de stock"),
    incluir_ventas: bool = Query(True, description="Incluir historial de ventas"),
    almacen_id: Optional[int] = Query(None, description="Filtrar por almacén específico"),
    reporte_service: ReporteService = Depends(get_reporte_service)
):
    """
    Genera un reporte de trazabilidad completa de un producto
    consolidando datos de almacén, tienda y catálogo
    """
    logger.info(f"Generando trazabilidad producto - producto_id: {producto_id}")
    
    # Validar parámetros de fecha
    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        raise ParametrosInvalidosError("La fecha desde debe ser anterior a fecha hasta")
    
    try:
        resultado = await reporte_service.generar_trazabilidad_producto(
            producto_id=producto_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            incluir_movimientos=incluir_movimientos,
            incluir_ventas=incluir_ventas,
            almacen_id=almacen_id
        )
        
        logger.info(f"Trazabilidad producto generada - {len(resultado.movimientos)} movimientos, {len(resultado.ventas)} ventas")
        return resultado
        
    except Exception as e:
        logger.error(f"Error generando trazabilidad producto: {str(e)}")
        raise

@router.get(
    "/health",
    summary="Health Check",
    description="Verifica el estado del servicio de reportes y servicios dependientes"
)
async def health_check(
    reporte_service: ReporteService = Depends(get_reporte_service)
):
    """
    Endpoint de salud que verifica la conectividad con servicios externos
    """
    try:
        # Verificar conectividad con servicios externos
        health_status = await reporte_service.verificar_salud_servicios()
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": health_status
            }
        )
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )
