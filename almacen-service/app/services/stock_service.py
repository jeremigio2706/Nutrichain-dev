"""
Servicio para gestión de stock (SOLO CONSULTAS Y REPORTES)

PRINCIPIO DE RESPONSABILIDAD ÚNICA Y AUDITABILIDAD:
- Este servicio SOLO se encarga de consultas y reportes de stock
- NO modifica cantidades de stock directamente  
- NO tiene métodos de escritura para evitar "puertas traseras"
- Toda modificación debe ser auditada via MovimientoService

ARQUITECTURA LIMPIA NIVEL SENIOR:
- Separación estricta de responsabilidades
- Imposible usar incorrectamente (fail-safe design)
- Integración con servicio de catálogo para validaciones
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy.orm import Session

from ..repositories.stock_repository import StockRepository
from ..repositories.almacen_repository import AlmacenRepository
from ..services.catalogo_integration_service import catalogo_service
from ..dtos.stock_dto import (
    StockResponseDTO,
    StockResumenDTO,
    StockConsolidadoDTO,
    StockDisponibilidadDTO,
    StockDisponibilidadResponseDTO,
    StockListDTO
)
from ..models.stock import Stock
from ..exceptions.api_exceptions import NotFoundError, ValidationError, BusinessLogicError


class StockService:
    """
    Servicio para gestión de stock (SOLO CONSULTAS Y REPORTES)
    
    DISEÑO FAIL-SAFE:
    - Sin métodos de escritura para prevenir modificaciones no auditadas
    - Integración con catálogo para validar existencia de productos
    - Consultas optimizadas con filtros dinámicos
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.stock_repository = StockRepository(db)
        self.almacen_repository = AlmacenRepository(db)
    
    # =====================================================================
    # MÉTODOS DE CONSULTA ÚNICAMENTE - DISEÑO FAIL-SAFE
    # =====================================================================
    # NOTA ARQUITECTÓNICA: No existen métodos de escritura en este servicio
    # para prevenir modificaciones no auditadas del inventario.
    # Todo cambio debe pasar por MovimientoService.
    
    def obtener_stock(self, stock_id: int) -> StockResponseDTO:
        """
        Obtener stock por ID (SOLO LECTURA)
        """
        stock = self.stock_repository.get(stock_id)
        if not stock:
            raise NotFoundError(f"Stock con ID {stock_id} no encontrado")
        
        return self._stock_to_dto(stock)
    
    def listar_stock(
        self, 
        almacen_id: Optional[int] = None,
        producto_id: Optional[int] = None,
        con_stock: Optional[bool] = None,
        limit: Optional[int] = 100,
        offset: int = 0
    ) -> StockListDTO:
        """Listar stock con filtros (SOLO LECTURA)"""
        filtros = {}
        if almacen_id:
            filtros['almacen_id'] = almacen_id
        if producto_id:
            filtros['producto_id'] = producto_id
        if con_stock is not None:
            if con_stock:
                filtros['cantidad_actual__gt'] = 0
            else:
                filtros['cantidad_actual'] = 0
        
        stocks, total = self.stock_repository.get_all_with_count(
            filtros=filtros,
            limit=limit,
            offset=offset
        )
        
        items = [self._stock_to_dto(stock) for stock in stocks]
        
        # Calcular paginación solo si limit no es None
        if limit is not None:
            page = offset // limit + 1
            has_next = (offset + limit) < total
        else:
            page = 1
            has_next = False
            limit = total  # Para mantener consistencia en la respuesta
        
        return StockListDTO(
            items=items,
            total=total,
            page=page,
            limit=limit,
            has_next=has_next,
            has_prev=offset > 0
        )
    
    def obtener_disponibilidad(self, disponibilidad_data: StockDisponibilidadDTO) -> StockDisponibilidadResponseDTO:
        """
        Consultar disponibilidad de productos (SOLO LECTURA)
        Implementación Senior: Valida existencia del producto en catálogo
        """
        # PASO 1: Validar que el producto existe en el catálogo
        # Como desarrollador senior, verificamos la integridad referencial
        producto_existe = catalogo_service.verificar_producto_existe_sync(disponibilidad_data.producto_id)
        
        if not producto_existe:
            raise NotFoundError(f"Producto no encontrado con ID: {disponibilidad_data.producto_id}")
        
        # PASO 2: Proceder con la consulta de disponibilidad
        almacenes_disponibles = []
        sugerencias = []
        
        if disponibilidad_data.almacen_id:
            # Consultar almacén específico
            stock = self.stock_repository.get_by_almacen_and_producto(
                disponibilidad_data.almacen_id, disponibilidad_data.producto_id
            )
            if stock:
                cantidad_disponible = stock.cantidad_actual - stock.cantidad_reservada
                puede_cubrir = cantidad_disponible >= disponibilidad_data.cantidad_requerida
                
                almacenes_disponibles.append({
                    "almacen_id": disponibilidad_data.almacen_id,
                    "almacen_nombre": f"Almacén {disponibilidad_data.almacen_id}",
                    "cantidad_disponible": cantidad_disponible,
                    "puede_cubrir": puede_cubrir
                })
                
                cantidad_disponible_total = cantidad_disponible
            else:
                cantidad_disponible_total = 0
                sugerencias.append(f"No hay stock del producto {disponibilidad_data.producto_id} en el almacén {disponibilidad_data.almacen_id}")
        else:
            # Consultar todos los almacenes
            stocks = self.stock_repository.get_by_producto(disponibilidad_data.producto_id)
            cantidad_disponible_total = 0
            
            for stock in stocks:
                cantidad_disponible = stock.cantidad_actual - stock.cantidad_reservada
                cantidad_disponible_total += cantidad_disponible
                puede_cubrir = cantidad_disponible >= disponibilidad_data.cantidad_requerida
                
                almacenes_disponibles.append({
                    "almacen_id": stock.almacen_id,
                    "almacen_nombre": f"Almacén {stock.almacen_id}",
                    "cantidad_disponible": cantidad_disponible,
                    "puede_cubrir": puede_cubrir
                })
        
        # Evaluar disponibilidad general
        disponible = cantidad_disponible_total >= disponibilidad_data.cantidad_requerida
        
        if not disponible:
            faltante = disponibilidad_data.cantidad_requerida - cantidad_disponible_total
            sugerencias.append(f"Faltan {faltante} unidades para cubrir la demanda")
            
        return StockDisponibilidadResponseDTO(
            producto_id=disponibilidad_data.producto_id,
            cantidad_requerida=disponibilidad_data.cantidad_requerida,
            cantidad_disponible_total=cantidad_disponible_total,
            disponible=disponible,
            almacenes_disponibles=almacenes_disponibles,
            sugerencias=sugerencias
        )
    
    def obtener_stock_consolidado(self, almacen_id: Optional[int] = None) -> List[StockConsolidadoDTO]:
        """Obtener resumen consolidado de stock (SOLO LECTURA)"""
        if almacen_id:
            stocks = self.stock_repository.get_by_filters({'almacen_id': almacen_id})
        else:
            stocks = self.stock_repository.get_multi(skip=0, limit=10000)  # Obtener todos los stocks
        
        # Consolidar por producto
        consolidado = {}
        for stock in stocks:
            producto_id = stock.producto_id
            if producto_id not in consolidado:
                consolidado[producto_id] = {
                    'producto_id': producto_id,
                    'cantidad_total': Decimal('0'),
                    'cantidad_disponible_total': Decimal('0'),
                    'almacenes_con_stock': 0,
                    'almacenes_sin_stock': 0,
                    'valor_total': Decimal('0'),
                    'detalle_almacenes': []
                }
            
            # Actualizar totales
            consolidado[producto_id]['cantidad_total'] += stock.cantidad_actual
            cantidad_disponible = stock.cantidad_actual - stock.cantidad_reservada
            consolidado[producto_id]['cantidad_disponible_total'] += cantidad_disponible
            consolidado[producto_id]['valor_total'] += stock.cantidad_actual * (stock.costo_unitario or Decimal('0'))
            
            # Contar almacenes
            if stock.cantidad_actual > 0:
                consolidado[producto_id]['almacenes_con_stock'] += 1
            else:
                consolidado[producto_id]['almacenes_sin_stock'] += 1
            
            # Agregar detalle del almacén
            consolidado[producto_id]['detalle_almacenes'].append(StockResumenDTO(
                producto_id=stock.producto_id,
                almacen_id=stock.almacen_id,
                almacen_nombre=f"Almacén {stock.almacen_id}",
                cantidad_actual=stock.cantidad_actual,
                cantidad_disponible=cantidad_disponible,
                cantidad_minima=stock.cantidad_minima,
                estado_stock="disponible" if cantidad_disponible > 0 else "sin_stock",
                valor_total=stock.cantidad_actual * (stock.costo_unitario or Decimal('0')),
                requiere_atencion=stock.cantidad_minima and stock.cantidad_actual <= stock.cantidad_minima
            ))
        
        return [StockConsolidadoDTO(**data) for data in consolidado.values()]
    
    def _stock_to_dto(self, stock: Stock) -> StockResponseDTO:
        """Convertir modelo Stock a DTO (HELPER PRIVADO)"""
        from datetime import date
        
        # Calcular campos derivados
        cantidad_disponible = stock.cantidad_disponible
        
        # Determinar estado del stock
        if cantidad_disponible <= 0:
            estado_stock = "sin_stock"
        elif stock.cantidad_minima and stock.cantidad_actual <= stock.cantidad_minima:
            estado_stock = "bajo_stock"
        elif stock.cantidad_maxima and stock.cantidad_actual >= stock.cantidad_maxima:
            estado_stock = "sobrecarga"
        else:
            estado_stock = "disponible"
        
        # Calcular días para vencimiento
        dias_para_vencimiento = None
        if stock.fecha_vencimiento:
            delta = stock.fecha_vencimiento - date.today()
            dias_para_vencimiento = delta.days
        
        # Calcular valor total
        valor_total = None
        if stock.costo_unitario:
            valor_total = stock.cantidad_actual * stock.costo_unitario
        
        return StockResponseDTO(
            id=stock.id,
            almacen_id=stock.almacen_id,
            producto_id=stock.producto_id,
            cantidad_actual=stock.cantidad_actual,
            cantidad_reservada=stock.cantidad_reservada,
            cantidad_disponible=cantidad_disponible,
            cantidad_minima=stock.cantidad_minima,
            cantidad_maxima=stock.cantidad_maxima,
            ubicacion_fisica=stock.ubicacion_fisica,
            lote=stock.lote,
            fecha_vencimiento=stock.fecha_vencimiento,
            costo_unitario=stock.costo_unitario,
            updated_at=stock.updated_at,
            estado_stock=estado_stock,
            dias_para_vencimiento=dias_para_vencimiento,
            valor_total=valor_total
        )
