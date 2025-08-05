"""
Repositorio para la gestión de almacenes
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from decimal import Decimal

from .base_repository import BaseRepository
from ..models.almacen import Almacen
from ..models.stock import Stock
from ..models.movimiento import Movimiento
from ..dtos.almacen_dto import AlmacenCreateDTO as AlmacenCreate, AlmacenUpdateDTO as AlmacenUpdate
from ..dtos import AlmacenFiltrosDTO

class AlmacenRepository(BaseRepository[Almacen, AlmacenCreate, AlmacenUpdate]):
    """Repositorio para operaciones de almacén"""
    
    def __init__(self, db: Session):
        super().__init__(db, Almacen)
    
    def get_by_codigo(self, codigo: str) -> Optional[Almacen]:
        """Obtener almacén por código"""
        return self.db.query(Almacen).filter(Almacen.codigo == codigo).first()
    
    def get_activos(self, skip: int = 0, limit: int = 100) -> List[Almacen]:
        """Obtener almacenes activos"""
        return self.db.query(Almacen).filter(
            Almacen.activo == True
        ).offset(skip).limit(limit).all()
    
    def buscar_por_filtros(self, filtros: AlmacenFiltrosDTO) -> List[Almacen]:
        """Buscar almacenes por filtros"""
        query = self.db.query(Almacen)
        
        if filtros.nombre:
            query = query.filter(Almacen.nombre.ilike(f"%{filtros.nombre}%"))
        
        if filtros.codigo:
            query = query.filter(Almacen.codigo.ilike(f"%{filtros.codigo}%"))
        
        if filtros.tipo:
            query = query.filter(Almacen.tipo == filtros.tipo)
        
        if filtros.responsable:
            query = query.filter(Almacen.responsable.ilike(f"%{filtros.responsable}%"))
        
        if filtros.activo is not None:
            query = query.filter(Almacen.activo == filtros.activo)
        
        return query.offset(filtros.skip).limit(filtros.limit).all()
    
    def contar_por_filtros(self, filtros: AlmacenFiltrosDTO) -> int:
        """Contar almacenes por filtros"""
        query = self.db.query(Almacen)
        
        if filtros.nombre:
            query = query.filter(Almacen.nombre.ilike(f"%{filtros.nombre}%"))
        
        if filtros.codigo:
            query = query.filter(Almacen.codigo.ilike(f"%{filtros.codigo}%"))
        
        if filtros.tipo:
            query = query.filter(Almacen.tipo == filtros.tipo)
        
        if filtros.responsable:
            query = query.filter(Almacen.responsable.ilike(f"%{filtros.responsable}%"))
        
        if filtros.activo is not None:
            query = query.filter(Almacen.activo == filtros.activo)
        
        return query.count()
    
    def get_con_estadisticas(self, almacen_id: int) -> Optional[Dict[str, Any]]:
        """Obtener almacén con estadísticas"""
        almacen = self.get(almacen_id)
        if not almacen:
            return None
        
        # Calcular estadísticas
        stats = self.db.query(
            func.count(Stock.id).label('total_productos'),
            func.coalesce(func.sum(Stock.cantidad_actual), 0).label('total_stock'),
            func.coalesce(func.sum(Stock.cantidad_actual * Stock.costo_unitario), 0).label('valor_inventario'),
            func.count(func.nullif(Stock.cantidad_actual <= Stock.cantidad_minima, False)).label('productos_bajo_stock'),
            func.count(func.nullif(Stock.cantidad_actual <= 0, False)).label('productos_sin_stock')
        ).filter(Stock.almacen_id == almacen_id).first()
        
        # Movimientos del mes actual
        inicio_mes = func.date_trunc('month', func.current_date())
        movimientos_mes = self.db.query(func.count(Movimiento.id)).filter(
            or_(
                Movimiento.almacen_origen_id == almacen_id,
                Movimiento.almacen_destino_id == almacen_id
            ),
            Movimiento.fecha_movimiento >= inicio_mes
        ).scalar()
        
        # Último movimiento
        ultimo_movimiento = self.db.query(Movimiento.fecha_movimiento).filter(
            or_(
                Movimiento.almacen_origen_id == almacen_id,
                Movimiento.almacen_destino_id == almacen_id
            )
        ).order_by(Movimiento.fecha_movimiento.desc()).first()
        
        return {
            'almacen': almacen,
            'total_productos': stats.total_productos or 0,
            'total_stock': stats.total_stock or Decimal('0'),
            'valor_inventario': stats.valor_inventario or Decimal('0'),
            'productos_bajo_stock': stats.productos_bajo_stock or 0,
            'productos_sin_stock': stats.productos_sin_stock or 0,
            'movimientos_mes': movimientos_mes or 0,
            'ultimo_movimiento': ultimo_movimiento[0] if ultimo_movimiento else None
        }
    
    def verificar_stock_activo(self, almacen_id: int) -> bool:
        """Verificar si el almacén tiene stock activo"""
        stock_count = self.db.query(func.count(Stock.id)).filter(
            Stock.almacen_id == almacen_id,
            Stock.cantidad_actual > 0
        ).scalar()
        
        return stock_count > 0
    
    def get_por_tipo(self, tipo: str) -> List[Almacen]:
        """Obtener almacenes por tipo"""
        return self.db.query(Almacen).filter(
            Almacen.tipo == tipo,
            Almacen.activo == True
        ).all()
    
    def get_por_responsable(self, responsable: str) -> List[Almacen]:
        """Obtener almacenes por responsable"""
        return self.db.query(Almacen).filter(
            Almacen.responsable.ilike(f"%{responsable}%"),
            Almacen.activo == True
        ).all()
    
    def existe_codigo(self, codigo: str, excluir_id: Optional[int] = None) -> bool:
        """Verificar si existe un código (excluyendo opcionalmente un ID)"""
        query = self.db.query(Almacen).filter(Almacen.codigo == codigo)
        
        if excluir_id:
            query = query.filter(Almacen.id != excluir_id)
        
        return query.first() is not None
    
    def existe_nombre(self, nombre: str, excluir_id: Optional[int] = None) -> bool:
        """Verificar si existe un nombre (excluyendo opcionalmente un ID)"""
        query = self.db.query(Almacen).filter(Almacen.nombre == nombre)
        
        if excluir_id:
            query = query.filter(Almacen.id != excluir_id)
        
        return query.first() is not None
