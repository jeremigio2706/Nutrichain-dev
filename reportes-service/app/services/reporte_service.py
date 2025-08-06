# =============================================================
# reporte_service.py
#
# Servicio de consolidación de datos para reportes. Orquesta consultas
# a múltiples microservicios para generar reportes unificados sin
# mantener estado propio.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

import httpx
import logging
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, date, timedelta

from ..dtos.reporte_dto import (
    StockValorizadoResponseDTO, StockValorizadoItemDTO,
    PedidosClienteResponseDTO, PedidoClienteDTO, PedidoClienteItemDTO,
    TrazabilidadProductoResponseDTO, MovimientoTrazabilidadDTO, PedidoTrazabilidadDTO,
    VentasReporteResponseDTO, VentasResumenDTO,
    ReporteParametrosDTO
)
from ..config import settings
from ..exceptions.api_exceptions import ServicioExternoError, ReporteError

logger = logging.getLogger(__name__)

class ReporteService:
    """Servicio para generación de reportes consolidados"""
    
    def __init__(self):
        self.almacen_base_url = f"{settings.almacen_service_url}/api/v1"
        self.tienda_base_url = f"{settings.tienda_service_url}"
        self.catalogo_base_url = f"{settings.catalogo_service_url}/api"
        self.timeout = 10.0
        
        # Logs para debug de URLs
        logger.info(f"URLs configuradas:")
        logger.info(f"  - almacen_service_url: {settings.almacen_service_url}")
        logger.info(f"  - tienda_service_url: {settings.tienda_service_url}")
        logger.info(f"  - catalogo_service_url: {settings.catalogo_service_url}")
        logger.info(f"URLs base construidas:")
        logger.info(f"  - almacen_base_url: {self.almacen_base_url}")
        logger.info(f"  - tienda_base_url: {self.tienda_base_url}")
        logger.info(f"  - catalogo_base_url: {self.catalogo_base_url}")
    
    async def generar_stock_valorizado(
        self, 
        almacen_id: Optional[int] = None,
        incluir_sin_stock: bool = False,
        categoria_id: Optional[int] = None
    ) -> StockValorizadoResponseDTO:
        """Generar reporte de stock valorizado"""
        logger.info(f"Generando reporte stock valorizado - almacen_id: {almacen_id}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Obtener datos de stock del servicio de almacén
                params = {}
                if almacen_id:
                    params["almacen_id"] = almacen_id
                
                logger.info(f"Obteniendo stock de: {self.almacen_base_url}/stock/")
                stock_response = await client.get(
                    f"{self.almacen_base_url}/stock/",
                    params=params
                )
                stock_response.raise_for_status()
                stock_data = stock_response.json()
                
                logger.info(f"Stock obtenido: {len(stock_data.get('items', []))} items")
                
                items_valorizados = []
                valor_total_inventario = Decimal('0')
                
                for item in stock_data.get("items", []):
                    try:
                        # Convertir cantidad_actual a Decimal para comparaciones
                        cantidad_actual = Decimal(str(item["cantidad_actual"]))
                        
                        # Filtrar por stock si no se incluyen sin stock
                        if not incluir_sin_stock and cantidad_actual <= 0:
                            continue
                        
                        logger.info(f"Obteniendo producto: {item['producto_id']}")
                        producto_response = await client.get(
                            f"{self.catalogo_base_url}/productos/{item['producto_id']}"
                        )
                        
                        if producto_response.status_code != 200:
                            logger.warning(f"No se pudo obtener producto {item['producto_id']}: {producto_response.status_code}")
                            continue
                            
                        producto_data = producto_response.json()
                        
                        # El catálogo envuelve la respuesta en {"success": true, "data": {...}}
                        producto_info = producto_data.get("data", {}) if producto_data.get("success") else {}
                        logger.info(f"Producto obtenido: {producto_info.get('nombre', 'Sin nombre')}")
                        
                        # Filtrar por categoría si se especifica
                        if categoria_id and producto_info.get("categoria") != categoria_id:
                            continue
                        
                        costo_unitario = (
                            Decimal(str(item.get("costo_unitario", 0))) 
                            if item.get("costo_unitario") else Decimal('0')
                        )
                        valor_total = costo_unitario * cantidad_actual
                        valor_total_inventario += valor_total
                        
                        items_valorizados.append(StockValorizadoItemDTO(
                            producto_id=item["producto_id"],
                            sku=producto_info.get("sku", ""),
                            nombre_producto=producto_info.get("nombre", ""),
                            categoria=producto_info.get("categoria", "Sin categoría"),
                            almacen_id=item["almacen_id"],
                            almacen_nombre="Almacén Principal",
                            cantidad_actual=cantidad_actual,
                            costo_unitario=costo_unitario,
                            valor_total=valor_total,
                            estado_stock=item.get("estado_stock", "disponible"),
                            ultima_actualizacion=datetime.now()
                        ))
                        
                    except Exception as e:
                        logger.error(f"Error procesando item {item.get('producto_id', 'unknown')}: {str(e)}")
                        continue
                
                resumen = {
                    "total_productos_diferentes": len(items_valorizados),
                    "cantidad_total_items": sum(float(item.cantidad_actual) for item in items_valorizados),
                    "valor_promedio_por_producto": (
                        float(valor_total_inventario / len(items_valorizados)) 
                        if items_valorizados else 0.0
                    )
                }
                
                logger.info(f"Reporte generado: {len(items_valorizados)} productos, valor total: {valor_total_inventario}")
                
                return StockValorizadoResponseDTO(
                    items=items_valorizados,
                    resumen=resumen,
                    fecha_reporte=datetime.now(),
                    total_productos=len(items_valorizados),
                    valor_total_inventario=valor_total_inventario
                )
                
            except httpx.RequestError as e:
                logger.error(f"Error de conexión: {str(e)}")
                raise ServicioExternoError("almacen", f"Error de conexión: {str(e)}")
            except Exception as e:
                logger.error(f"Error generando reporte de stock: {str(e)}")
                raise ReporteError(f"Error generando reporte de stock: {str(e)}")
    
    async def generar_pedidos_cliente(
        self,
        cliente_id: int,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        estado: Optional[str] = None,
        incluir_detalles: bool = True
    ) -> PedidosClienteResponseDTO:
        """Generar reporte de pedidos por cliente"""
        logger.info(f"Generando reporte pedidos cliente - cliente_id: {cliente_id}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Obtener pedidos del cliente desde el servicio de tienda
                params = {"cliente_id": cliente_id}
                if fecha_desde:
                    params["fecha_desde"] = fecha_desde.isoformat()
                if fecha_hasta:
                    params["fecha_hasta"] = fecha_hasta.isoformat()
                if estado:
                    params["estado"] = estado
                
                pedidos_response = await client.get(
                    f"{self.tienda_base_url}/pedidos/",
                    params=params
                )
                pedidos_response.raise_for_status()
                pedidos_data = pedidos_response.json()
                
                pedidos_procesados = []
                for pedido in pedidos_data.get("pedidos", []):
                    items = []
                    if incluir_detalles:
                        for item in pedido.get("items", []):
                            # Enriquecer con datos del catálogo
                            try:
                                producto_response = await client.get(
                                    f"{self.catalogo_base_url}/productos/{item['producto_id']}"
                                )
                                if producto_response.status_code == 200:
                                    producto_data = producto_response.json()
                                    item["nombre_producto"] = producto_data.get("nombre", "Sin nombre")
                                    item["categoria"] = producto_data.get("categoria", "Sin categoría")
                            except:
                                item["nombre_producto"] = "Sin nombre"
                                item["categoria"] = "Sin categoría"
                            
                            items.append(PedidoClienteItemDTO(
                                producto_id=item["producto_id"],
                                nombre_producto=item.get("nombre_producto", "Sin nombre"),
                                cantidad=Decimal(str(item["cantidad"])),
                                precio_unitario=Decimal(str(item["precio_unitario"])),
                                subtotal=Decimal(str(item["subtotal"]))
                            ))
                    
                    pedidos_procesados.append(PedidoClienteDTO(
                        pedido_id=pedido["id"],
                        fecha_pedido=datetime.fromisoformat(pedido["fecha_pedido"].replace('Z', '+00:00')),
                        estado=pedido["estado"],
                        total=Decimal(str(pedido["total"])),
                        items=items
                    ))
                
                # Calcular resumen
                total_pedidos = len(pedidos_procesados)
                monto_total = sum(pedido.total for pedido in pedidos_procesados)
                monto_promedio = monto_total / total_pedidos if total_pedidos > 0 else Decimal('0')
                
                return PedidosClienteResponseDTO(
                    cliente_id=cliente_id,
                    pedidos=pedidos_procesados,
                    resumen={
                        "total_pedidos": total_pedidos,
                        "monto_total": float(monto_total),
                        "monto_promedio": float(monto_promedio),
                        "estados": {}
                    },
                    fecha_inicio=fecha_desde,
                    fecha_fin=fecha_hasta
                )
                
            except httpx.RequestError as e:
                raise ServicioExternoError("tienda", f"Error de conexión: {str(e)}")
            except Exception as e:
                raise ReporteError(f"Error generando pedidos cliente: {str(e)}")
    
    async def generar_trazabilidad_producto(
        self,
        producto_id: int,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        incluir_movimientos: bool = True,
        incluir_ventas: bool = True,
        almacen_id: Optional[int] = None
    ) -> TrazabilidadProductoResponseDTO:
        """Generar reporte de trazabilidad de producto"""
        logger.info(f"Generando trazabilidad producto - producto_id: {producto_id}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Obtener información del producto
                producto_response = await client.get(
                    f"{self.catalogo_base_url}/productos/{producto_id}"
                )
                producto_response.raise_for_status()
                producto_data = producto_response.json()
                
                movimientos = []
                pedidos = []
                
                if incluir_movimientos:
                    # Obtener movimientos de stock
                    params = {"producto_id": producto_id}
                    if almacen_id:
                        params["almacen_id"] = almacen_id
                    if fecha_desde:
                        params["fecha_desde"] = fecha_desde.isoformat()
                    if fecha_hasta:
                        params["fecha_hasta"] = fecha_hasta.isoformat()
                    
                    movimientos_response = await client.get(
                        f"{self.almacen_base_url}/movimientos/",
                        params=params
                    )
                    if movimientos_response.status_code == 200:
                        movimientos_data = movimientos_response.json()
                        for mov in movimientos_data.get("movimientos", []):
                            movimientos.append(MovimientoTrazabilidadDTO(
                                fecha=datetime.fromisoformat(mov["fecha"].replace('Z', '+00:00')),
                                tipo_movimiento=mov["tipo_movimiento"],
                                cantidad=Decimal(str(mov["cantidad"])),
                                almacen_origen=mov.get("almacen_origen"),
                                almacen_destino=mov.get("almacen_destino"),
                                usuario=mov.get("usuario", "Sistema"),
                                observaciones=mov.get("observaciones", "")
                            ))
                
                if incluir_ventas:
                    # Obtener pedidos que incluyen este producto
                    params = {"producto_id": producto_id}
                    if fecha_desde:
                        params["fecha_desde"] = fecha_desde.isoformat()
                    if fecha_hasta:
                        params["fecha_hasta"] = fecha_hasta.isoformat()
                    
                    pedidos_response = await client.get(
                        f"{self.tienda_base_url}/pedidos/",
                        params=params
                    )
                    if pedidos_response.status_code == 200:
                        pedidos_data = pedidos_response.json()
                        for pedido in pedidos_data.get("pedidos", []):
                            # Buscar items que correspondan a este producto
                            for item in pedido.get("items", []):
                                if item["producto_id"] == producto_id:
                                    pedidos.append(PedidoTrazabilidadDTO(
                                        pedido_id=pedido["id"],
                                        fecha=datetime.fromisoformat(pedido["fecha_pedido"].replace('Z', '+00:00')),
                                        cliente_id=pedido["cliente_id"],
                                        cantidad=Decimal(str(item["cantidad"])),
                                        precio_unitario=Decimal(str(item["precio_unitario"])),
                                        subtotal=Decimal(str(item["subtotal"])),
                                        estado=pedido["estado"]
                                    ))
                
                return TrazabilidadProductoResponseDTO(
                    producto_id=producto_id,
                    nombre_producto=producto_data.get("nombre", "Sin nombre"),
                    sku=producto_data.get("sku", ""),
                    movimientos=movimientos,
                    ventas=pedidos,
                    resumen={
                        "total_movimientos": len(movimientos),
                        "total_ventas": len(pedidos),
                        "cantidad_total_vendida": sum(float(p.cantidad) for p in pedidos),
                        "ingresos_totales": sum(float(p.subtotal) for p in pedidos)
                    },
                    fecha_inicio=fecha_desde,
                    fecha_fin=fecha_hasta
                )
                
            except httpx.RequestError as e:
                raise ServicioExternoError("consolidacion", f"Error de conexión: {str(e)}")
            except Exception as e:
                raise ReporteError(f"Error generando trazabilidad: {str(e)}")
    
    async def verificar_salud_servicios(self) -> Dict[str, str]:
        """Verificar la salud de los servicios externos"""
        servicios = {
            "almacen": f"{settings.almacen_service_url}/health",
            "tienda": f"{settings.tienda_service_url}/health", 
            "catalogo": f"{settings.catalogo_service_url}/api/status"
        }
        
        logger.info(f"Verificando salud de servicios con URLs:")
        for servicio, url in servicios.items():
            logger.info(f"  - {servicio}: {url}")
        
        status = {}
        
        for servicio, url in servicios.items():
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    logger.info(f"Conectando a {servicio} en {url}")
                    response = await client.get(url)
                    status[servicio] = "healthy" if response.status_code == 200 else "unhealthy"
                    logger.info(f"Respuesta de {servicio}: {response.status_code}")
            except Exception as e:
                logger.error(f"Error conectando a {servicio}: {str(e)}")
                status[servicio] = "unhealthy"
        
        logger.info(f"Estado final de servicios: {status}")
        return status
