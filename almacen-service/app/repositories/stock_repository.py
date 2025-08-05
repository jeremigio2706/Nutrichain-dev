"""
Repositorio para gestión de stock
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from .base_repository import BaseRepository
from ..models.stock import Stock
from ..dtos.stock_dto import StockCreateDTO as StockCreate, StockUpdateDTO as StockUpdate


class StockRepository(BaseRepository[Stock, StockCreate, StockUpdate]):
    """Repositorio para gestión de stock"""
    
    def __init__(self, db: Session):
        super().__init__(db, Stock)
    
    def get_by_almacen_and_producto(self, almacen_id: int, producto_id: int) -> Optional[Stock]:
        """Obtener stock por almacén y producto"""
        return self.db.query(Stock).filter(
            and_(
                Stock.almacen_id == almacen_id,
                Stock.producto_id == producto_id
            )
        ).first()
    
    def get_by_producto(self, producto_id: int) -> List[Stock]:
        """Obtener todos los stocks de un producto"""
        return self.db.query(Stock).filter(
            Stock.producto_id == producto_id
        ).all()
    
    def get_by_almacen(self, almacen_id: int) -> List[Stock]:
        """Obtener stock por almacén"""
        return self.db.query(Stock).filter(
            Stock.almacen_id == almacen_id
        ).all()
    
    def get_by_producto(self, producto_id: int) -> List[Stock]:
        """Obtener stock por producto"""
        return self.db.query(Stock).filter(
            Stock.producto_id == producto_id
        ).all()
    
    def get_by_producto_y_almacen(self, producto_id: int, almacen_id: int) -> Optional[Stock]:
        """Obtener stock específico por producto y almacén"""
        return self.db.query(Stock).filter(
            Stock.producto_id == producto_id,
            Stock.almacen_id == almacen_id
        ).first()
    
    def get_stock_bajo(self, almacen_id: Optional[int] = None) -> List[Stock]:
        """Obtener productos con stock bajo"""
        query = self.db.query(Stock).filter(
            Stock.cantidad_actual <= Stock.cantidad_minima
        )
        
        if almacen_id:
            query = query.filter(Stock.almacen_id == almacen_id)
            
        return query.all()
    
    def get_with_low_stock(self, almacen_id: Optional[int] = None) -> List[Stock]:
        """Obtener productos con stock bajo (cantidad actual < cantidad mínima)"""
        query = self.db.query(Stock).filter(
            Stock.cantidad_actual < Stock.cantidad_minima
        )
        
        if almacen_id:
            query = query.filter(Stock.almacen_id == almacen_id)
        
        return query.all()
    
    def get_stock_agotado(self, almacen_id: Optional[int] = None) -> List[Stock]:
        """Obtener productos sin stock"""
        query = self.db.query(Stock).filter(Stock.cantidad_actual <= 0)
        
        if almacen_id:
            query = query.filter(Stock.almacen_id == almacen_id)
            
        return query.all()
    
    def get_by_filters(
        self,
        filtros: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> List[Stock]:
        """Obtener stock con filtros dinámicos"""
        query = self.db.query(Stock)
        
        # Aplicar filtros
        for field, value in filtros.items():
            if field.endswith('__gt'):
                # Mayor que
                real_field = field.replace('__gt', '')
                if hasattr(Stock, real_field):
                    query = query.filter(getattr(Stock, real_field) > value)
            elif field.endswith('__gte'):
                # Mayor o igual que
                real_field = field.replace('__gte', '')
                if hasattr(Stock, real_field):
                    query = query.filter(getattr(Stock, real_field) >= value)
            elif field.endswith('__lt'):
                # Menor que
                real_field = field.replace('__lt', '')
                if hasattr(Stock, real_field):
                    query = query.filter(getattr(Stock, real_field) < value)
            elif field.endswith('__lte'):
                # Menor o igual que
                real_field = field.replace('__lte', '')
                if hasattr(Stock, real_field):
                    query = query.filter(getattr(Stock, real_field) <= value)
            elif field.endswith('__like'):
                # LIKE para strings
                real_field = field.replace('__like', '')
                if hasattr(Stock, real_field):
                    query = query.filter(getattr(Stock, real_field).like(f"%{value}%"))
            else:
                # Igualdad exacta
                if hasattr(Stock, field):
                    query = query.filter(getattr(Stock, field) == value)
        
        # Aplicar ordenamiento
        if order_by:
            if order_by.startswith('-'):
                # Orden descendente
                field_name = order_by[1:]
                if hasattr(Stock, field_name):
                    query = query.order_by(desc(getattr(Stock, field_name)))
            else:
                # Orden ascendente
                if hasattr(Stock, order_by):
                    query = query.order_by(getattr(Stock, order_by))
        else:
            query = query.order_by(Stock.id)
        
        # Aplicar paginación
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_all_with_count(
        self,
        filtros: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> Tuple[List[Stock], int]:
        """Obtener stock con filtros y conteo total"""
        # Consulta base
        base_query = self.db.query(Stock)
        
        # Aplicar filtros si existen
        if filtros:
            for field, value in filtros.items():
                if field.endswith('__gt'):
                    real_field = field.replace('__gt', '')
                    if hasattr(Stock, real_field):
                        base_query = base_query.filter(getattr(Stock, real_field) > value)
                elif field.endswith('__gte'):
                    real_field = field.replace('__gte', '')
                    if hasattr(Stock, real_field):
                        base_query = base_query.filter(getattr(Stock, real_field) >= value)
                elif field.endswith('__lt'):
                    real_field = field.replace('__lt', '')
                    if hasattr(Stock, real_field):
                        base_query = base_query.filter(getattr(Stock, real_field) < value)
                elif field.endswith('__lte'):
                    real_field = field.replace('__lte', '')
                    if hasattr(Stock, real_field):
                        base_query = base_query.filter(getattr(Stock, real_field) <= value)
                elif field.endswith('__like'):
                    real_field = field.replace('__like', '')
                    if hasattr(Stock, real_field):
                        base_query = base_query.filter(getattr(Stock, real_field).like(f"%{value}%"))
                else:
                    if hasattr(Stock, field):
                        base_query = base_query.filter(getattr(Stock, field) == value)
        
        # Conteo total
        total = base_query.count()
        
        # Aplicar ordenamiento
        if order_by:
            if order_by.startswith('-'):
                field_name = order_by[1:]
                if hasattr(Stock, field_name):
                    base_query = base_query.order_by(desc(getattr(Stock, field_name)))
            else:
                if hasattr(Stock, order_by):
                    base_query = base_query.order_by(getattr(Stock, order_by))
        else:
            base_query = base_query.order_by(Stock.id)
        
        # Aplicar paginación
        if offset:
            base_query = base_query.offset(offset)
        if limit:
            base_query = base_query.limit(limit)
        
        # Obtener resultados
        items = base_query.all()
        
        return items, total
    
    def get_stock_summary_by_almacen(self, almacen_id: int) -> Dict[str, Any]:
        """Obtener resumen de stock por almacén"""
        stocks = self.get_by_almacen(almacen_id)
        
        total_productos = len(stocks)
        productos_con_stock = len([s for s in stocks if s.cantidad_actual > 0])
        productos_sin_stock = total_productos - productos_con_stock
        productos_stock_bajo = len([s for s in stocks if s.cantidad_minima and s.cantidad_actual < s.cantidad_minima])
        
        return {
            "almacen_id": almacen_id,
            "total_productos": total_productos,
            "productos_con_stock": productos_con_stock,
            "productos_sin_stock": productos_sin_stock,
            "productos_stock_bajo": productos_stock_bajo,
            "total_cantidad": sum(s.cantidad_actual for s in stocks),
            "valor_total": sum(s.cantidad_actual * (s.costo_unitario or 0) for s in stocks)
        }
