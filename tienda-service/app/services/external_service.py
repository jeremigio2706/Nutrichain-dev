# ============================================================================
# external_service.py
#
# Servicio para comunicación con microservicios externos. Centraliza las
# llamadas HTTP a otros servicios del ecosistema como almacén y catálogo,
# implementando lógica de reintentos y manejo de errores.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

import httpx
import redis
import json
import time
from typing import List, Dict, Any, Optional
from decimal import Decimal

from ..config import settings
from ..exceptions.api_exceptions import ServicioExternoError

class ExternalService:
    """Servicio para comunicación con servicios externos"""
    
    def __init__(self):
        self.almacen_base_url = f"{settings.almacen_service_url}/api/v1"
        self.catalogo_base_url = f"{settings.catalogo_service_url}/api"
        self.redis_client = redis.from_url(settings.redis_url)
        self.timeout = 30.0
    
    async def consultar_disponibilidad_stock(self, productos: List[Dict]) -> Dict[str, Any]:
        """Consultar disponibilidad de stock en el servicio de almacén"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Consultar cada producto individualmente (principio KISS)
                resultados = []
                for producto in productos:
                    response = await client.get(
                        f"{self.almacen_base_url}/stock/",
                        params={
                            "producto_id": producto["producto_id"],
                            "almacen_id": producto["almacen_id"]
                        }
                    )
                    response.raise_for_status()
                    stock_data = response.json()
                    
                    if stock_data["items"]:
                        stock_info = stock_data["items"][0]
                        disponible = float(stock_info["cantidad_disponible"])
                        requerido = float(producto["cantidad"])
                        
                        resultados.append({
                            "producto_id": producto["producto_id"],
                            "almacen_id": producto["almacen_id"],
                            "cantidad_disponible": disponible,
                            "cantidad_requerida": requerido,
                            "disponible": disponible >= requerido
                        })
                    else:
                        resultados.append({
                            "producto_id": producto["producto_id"],
                            "almacen_id": producto["almacen_id"],
                            "cantidad_disponible": 0,
                            "cantidad_requerida": float(producto["cantidad"]),
                            "disponible": False
                        })
                
                return {"productos": resultados}
            except httpx.RequestError as e:
                raise ServicioExternoError("almacen", f"Error de conexión: {str(e)}")
            except httpx.HTTPStatusError as e:
                raise ServicioExternoError("almacen", f"Error HTTP {e.response.status_code}: {e.response.text}")
    
    async def crear_movimiento_salida(self, productos: List[Dict], motivo: str) -> Dict[str, Any]:
        """Crear uno o múltiples movimientos de salida en el servicio de almacén"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Preparar datos siguiendo el principio KISS
                if len(productos) == 1:
                    # Un solo movimiento - usar estructura simple
                    movimiento_data = {
                        "producto_id": productos[0]["producto_id"],
                        "almacen_origen_id": productos[0]["almacen_origen_id"],
                        "tipo_movimiento": "salida",
                        "cantidad": productos[0]["cantidad"],
                        "motivo": motivo,
                        "usuario": productos[0].get("usuario", "sistema")
                    }
                else:
                    # Múltiples movimientos - usar estructura de array
                    movimientos = []
                    for producto in productos:
                        movimientos.append({
                            "producto_id": producto["producto_id"],
                            "almacen_origen_id": producto["almacen_origen_id"],
                            "tipo_movimiento": "salida",
                            "cantidad": producto["cantidad"],
                            "motivo": f"{motivo} - Producto {producto['producto_id']}",
                            "usuario": producto.get("usuario", "sistema")
                        })
                    movimiento_data = {"movimientos": movimientos}
                
                response = await client.post(
                    f"{self.almacen_base_url}/movimientos/salida",
                    json=movimiento_data
                )
                response.raise_for_status()
                return {"success": True, "data": response.json()}
            except httpx.RequestError as e:
                raise ServicioExternoError("almacen", f"Error de conexión: {str(e)}")
            except httpx.HTTPStatusError as e:
                raise ServicioExternoError("almacen", f"Error HTTP {e.response.status_code}: {e.response.text}")
    
    async def crear_movimiento_entrada(self, productos: List[Dict], motivo: str) -> Dict[str, Any]:
        """Crear uno o múltiples movimientos de entrada en el servicio de almacén"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Preparar datos siguiendo el principio KISS
                if len(productos) == 1:
                    # Un solo movimiento
                    movimiento_data = {
                        "producto_id": productos[0]["producto_id"],
                        "almacen_destino_id": productos[0]["almacen_destino_id"],
                        "tipo_movimiento": "entrada",
                        "cantidad": productos[0]["cantidad"],
                        "motivo": motivo,
                        "costo_unitario": productos[0].get("costo_unitario"),
                        "usuario": productos[0].get("usuario", "sistema")
                    }
                else:
                    # Múltiples movimientos
                    movimientos = []
                    for producto in productos:
                        movimientos.append({
                            "producto_id": producto["producto_id"],
                            "almacen_destino_id": producto["almacen_destino_id"],
                            "tipo_movimiento": "entrada",
                            "cantidad": producto["cantidad"],
                            "motivo": f"{motivo} - Producto {producto['producto_id']}",
                            "costo_unitario": producto.get("costo_unitario"),
                            "usuario": producto.get("usuario", "sistema")
                        })
                    movimiento_data = {"movimientos": movimientos}
                
                response = await client.post(
                    f"{self.almacen_base_url}/movimientos/entrada",
                    json=movimiento_data
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise ServicioExternoError("almacen", f"Error de conexión: {str(e)}")
            except httpx.HTTPStatusError as e:
                raise ServicioExternoError("almacen", f"Error HTTP {e.response.status_code}: {e.response.text}")
    
    async def obtener_producto_catalogo(self, producto_id: int) -> Dict[str, Any]:
        """Obtener información de producto del catálogo"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(f"{self.catalogo_base_url}/productos/{producto_id}")
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise ServicioExternoError("catalogo", f"Error de conexión: {str(e)}")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise ServicioExternoError("catalogo", f"Producto {producto_id} no encontrado")
                raise ServicioExternoError("catalogo", f"Error HTTP {e.response.status_code}: {e.response.text}")
    
    async def obtener_productos_catalogo(self, producto_ids: List[int]) -> List[Dict[str, Any]]:
        """Obtener información de múltiples productos del catálogo"""
        productos = []
        for producto_id in producto_ids:
            try:
                producto = await self.obtener_producto_catalogo(producto_id)
                productos.append(producto)
            except ServicioExternoError:
                productos.append({"id": producto_id, "error": "No encontrado"})
        return productos
    
    def encolar_tarea_pedido(self, pedido_id: int, accion: str, datos: Dict[str, Any]) -> bool:
        """Encolar tarea relacionada con pedido en Redis"""
        try:
            tarea = {
                "pedido_id": pedido_id,
                "accion": accion,
                "datos": datos,
                "timestamp": str(time.time())
            }
            
            self.redis_client.lpush("cola_pedidos", json.dumps(tarea, default=str))
            return True
        except Exception as e:
            raise ServicioExternoError("redis", f"Error al encolar tarea: {str(e)}")
    
    def obtener_tarea_pedido(self) -> Optional[Dict[str, Any]]:
        """Obtener tarea de la cola de pedidos"""
        try:
            tarea_json = self.redis_client.brpop("cola_pedidos", timeout=1)
            if tarea_json:
                return json.loads(tarea_json[1])
            return None
        except Exception as e:
            raise ServicioExternoError("redis", f"Error al obtener tarea: {str(e)}")
    
    def marcar_pedido_procesando(self, pedido_id: int) -> bool:
        """Marcar pedido como en procesamiento en Redis"""
        try:
            self.redis_client.setex(f"pedido_procesando:{pedido_id}", 300, "true")
            return True
        except Exception as e:
            raise ServicioExternoError("redis", f"Error al marcar pedido: {str(e)}")
    
    def liberar_pedido_procesando(self, pedido_id: int) -> bool:
        """Liberar marca de procesamiento de pedido"""
        try:
            self.redis_client.delete(f"pedido_procesando:{pedido_id}")
            return True
        except Exception as e:
            raise ServicioExternoError("redis", f"Error al liberar pedido: {str(e)}")
    
    def esta_pedido_procesando(self, pedido_id: int) -> bool:
        """Verificar si un pedido está siendo procesado"""
        try:
            return self.redis_client.exists(f"pedido_procesando:{pedido_id}")
        except Exception as e:
            raise ServicioExternoError("redis", f"Error al verificar pedido: {str(e)}")
