"""
Repositorio para gestión de movimientos de inventario
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from .base_repository import BaseRepository
from ..models.movimiento import Movimiento
from ..dtos.movimiento_dto import MovimientoEntradaDTO as MovimientoCreate, MovimientoResponseDTO as MovimientoUpdate
from ..dtos.movimiento_dto import TipoMovimientoEnum, EstadoMovimientoEnum


class MovimientoRepository(BaseRepository[Movimiento, MovimientoCreate, MovimientoUpdate]):
    """Repositorio para gestión de movimientos de inventario"""
    
    def __init__(self, db: Session):
        super().__init__(db, Movimiento)
    
    async def get_by_stock_id(self, stock_id: int, limit: Optional[int] = None) -> List[Movimiento]:
        """Obtener movimientos por stock ID"""
        query = self.db.query(Movimiento).filter(Movimiento.stock_id == stock_id)
        
        if limit:
            query = query.limit(limit)
        
        return query.order_by(desc(Movimiento.fecha_movimiento)).all()
    
    def get_by_almacen(
        self, 
        almacen_id: int, 
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        tipo_movimiento: Optional[TipoMovimientoEnum] = None,
        skip: int = 0,
        limit: Optional[int] = None
    ) -> List[Movimiento]:
        """Obtener movimientos por almacén (origen o destino)"""
        query = self.db.query(Movimiento).filter(
            or_(
                Movimiento.almacen_origen_id == almacen_id,
                Movimiento.almacen_destino_id == almacen_id
            )
        )
        
        # Aplicar filtros de fecha
        if fecha_inicio:
            query = query.filter(Movimiento.fecha_movimiento >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Movimiento.fecha_movimiento <= fecha_fin)
        if tipo_movimiento:
            query = query.filter(Movimiento.tipo_movimiento == tipo_movimiento)
        
        # Aplicar orden ANTES de paginación
        query = query.order_by(desc(Movimiento.fecha_movimiento))
        
        # Aplicar paginación
        query = query.offset(skip)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def count_by_almacen(
        self, 
        almacen_id: int, 
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        tipo_movimiento: Optional[TipoMovimientoEnum] = None
    ) -> int:
        """Contar movimientos por almacén (origen o destino)"""
        query = self.db.query(Movimiento).filter(
            or_(
                Movimiento.almacen_origen_id == almacen_id,
                Movimiento.almacen_destino_id == almacen_id
            )
        )
        
        # Aplicar filtros de fecha
        if fecha_inicio:
            query = query.filter(Movimiento.fecha_movimiento >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Movimiento.fecha_movimiento <= fecha_fin)
        if tipo_movimiento:
            query = query.filter(Movimiento.tipo_movimiento == tipo_movimiento)
        
        return query.count()
    
    async def get_by_producto(self, producto_id: int, limit: Optional[int] = None) -> List[Movimiento]:
        """Obtener movimientos por producto"""
        query = self.db.query(Movimiento).filter(Movimiento.producto_id == producto_id)
        
        if limit:
            query = query.limit(limit)
        
        return query.order_by(desc(Movimiento.fecha_movimiento)).all()
    
    async def get_by_tipo(self, tipo_movimiento: TipoMovimientoEnum, limit: Optional[int] = None) -> List[Movimiento]:
        """Obtener movimientos por tipo"""
        query = self.db.query(Movimiento).filter(Movimiento.tipo_movimiento == tipo_movimiento)
        
        if limit:
            query = query.limit(limit)
        
        return query.order_by(desc(Movimiento.fecha_movimiento)).all()
    
    async def get_by_date_range(
        self,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        almacen_id: Optional[int] = None
    ) -> List[Movimiento]:
        """Obtener movimientos en un rango de fechas"""
        query = self.db.query(Movimiento).filter(
            and_(
                Movimiento.fecha_movimiento >= fecha_inicio,
                Movimiento.fecha_movimiento <= fecha_fin
            )
        )
        
        if almacen_id:
            query = query.filter(Movimiento.almacen_id == almacen_id)
        
        return query.order_by(desc(Movimiento.fecha_movimiento)).all()
    
    async def get_by_filters(
        self,
        filtros: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> List[Movimiento]:
        """Obtener movimientos con filtros dinámicos"""
        query = self.db.query(Movimiento)
        
        # Aplicar filtros
        for field, value in filtros.items():
            if hasattr(Movimiento, field):
                if field.endswith('__gte'):
                    # Mayor o igual que (para fechas)
                    real_field = field.replace('__gte', '')
                    if hasattr(Movimiento, real_field):
                        query = query.filter(getattr(Movimiento, real_field) >= value)
                elif field.endswith('__lte'):
                    # Menor o igual que (para fechas)
                    real_field = field.replace('__lte', '')
                    if hasattr(Movimiento, real_field):
                        query = query.filter(getattr(Movimiento, real_field) <= value)
                elif field.endswith('__like'):
                    # LIKE para strings
                    real_field = field.replace('__like', '')
                    if hasattr(Movimiento, real_field):
                        query = query.filter(getattr(Movimiento, real_field).like(f"%{value}%"))
                else:
                    # Igualdad exacta
                    query = query.filter(getattr(Movimiento, field) == value)
        
        # Aplicar ordenamiento
        if order_by:
            if order_by.startswith('-'):
                # Orden descendente
                field_name = order_by[1:]
                if hasattr(Movimiento, field_name):
                    query = query.order_by(desc(getattr(Movimiento, field_name)))
            else:
                # Orden ascendente
                if hasattr(Movimiento, order_by):
                    query = query.order_by(getattr(Movimiento, order_by))
        else:
            query = query.order_by(desc(Movimiento.fecha_movimiento))
        
        # Aplicar paginación
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    async def get_all_with_count(
        self,
        filtros: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> Tuple[List[Movimiento], int]:
        """Obtener movimientos con filtros y conteo total"""
        # Consulta base
        base_query = self.db.query(Movimiento)
        
        # Aplicar filtros si existen
        if filtros:
            for field, value in filtros.items():
                if hasattr(Movimiento, field):
                    if field.endswith('__gte'):
                        real_field = field.replace('__gte', '')
                        if hasattr(Movimiento, real_field):
                            base_query = base_query.filter(getattr(Movimiento, real_field) >= value)
                    elif field.endswith('__lte'):
                        real_field = field.replace('__lte', '')
                        if hasattr(Movimiento, real_field):
                            base_query = base_query.filter(getattr(Movimiento, real_field) <= value)
                    elif field.endswith('__like'):
                        real_field = field.replace('__like', '')
                        if hasattr(Movimiento, real_field):
                            base_query = base_query.filter(getattr(Movimiento, real_field).like(f"%{value}%"))
                    else:
                        base_query = base_query.filter(getattr(Movimiento, field) == value)
        
        # Conteo total
        total = base_query.count()
        
        # Aplicar ordenamiento
        if order_by:
            if order_by.startswith('-'):
                field_name = order_by[1:]
                if hasattr(Movimiento, field_name):
                    base_query = base_query.order_by(desc(getattr(Movimiento, field_name)))
            else:
                if hasattr(Movimiento, order_by):
                    base_query = base_query.order_by(getattr(Movimiento, order_by))
        else:
            base_query = base_query.order_by(desc(Movimiento.fecha_movimiento))
        
        # Aplicar paginación
        if offset:
            base_query = base_query.offset(offset)
        if limit:
            base_query = base_query.limit(limit)
        
        # Obtener resultados
        items = base_query.all()
        
        return items, total
    
    async def get_entradas_by_period(
        self,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        almacen_id: Optional[int] = None
    ) -> List[Movimiento]:
        """Obtener movimientos de entrada en un período"""
        query = self.db.query(Movimiento).filter(
            and_(
                Movimiento.tipo_movimiento.in_([
                    TipoMovimientoEnum.ENTRADA,
                    TipoMovimientoEnum.TRANSFERENCIA_ENTRADA
                ]),
                Movimiento.fecha_movimiento >= fecha_inicio,
                Movimiento.fecha_movimiento <= fecha_fin
            )
        )
        
        if almacen_id:
            query = query.filter(Movimiento.almacen_id == almacen_id)
        
        return query.order_by(desc(Movimiento.fecha_movimiento)).all()
    
    async def get_salidas_by_period(
        self,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        almacen_id: Optional[int] = None
    ) -> List[Movimiento]:
        """Obtener movimientos de salida en un período"""
        query = self.db.query(Movimiento).filter(
            and_(
                Movimiento.tipo_movimiento.in_([
                    TipoMovimientoEnum.SALIDA,
                    TipoMovimientoEnum.TRANSFERENCIA_SALIDA
                ]),
                Movimiento.fecha_movimiento >= fecha_inicio,
                Movimiento.fecha_movimiento <= fecha_fin
            )
        )
        
        if almacen_id:
            query = query.filter(Movimiento.almacen_id == almacen_id)
        
        return query.order_by(desc(Movimiento.fecha_movimiento)).all()
    
    async def get_movimientos_summary_by_almacen(
        self,
        almacen_id: int,
        fecha_inicio: Optional[datetime] = None,
        fecha_fin: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Obtener resumen de movimientos por almacén"""
        query = self.db.query(Movimiento).filter(Movimiento.almacen_id == almacen_id)
        
        if fecha_inicio:
            query = query.filter(Movimiento.fecha_movimiento >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Movimiento.fecha_movimiento <= fecha_fin)
        
        movimientos = query.all()
        
        entradas = [m for m in movimientos if m.tipo_movimiento in [
            TipoMovimientoEnum.ENTRADA, TipoMovimientoEnum.TRANSFERENCIA_ENTRADA
        ]]
        salidas = [m for m in movimientos if m.tipo_movimiento in [
            TipoMovimientoEnum.SALIDA, TipoMovimientoEnum.TRANSFERENCIA_SALIDA
        ]]
        
        return {
            "almacen_id": almacen_id,
            "periodo": {
                "fecha_inicio": fecha_inicio.isoformat() if fecha_inicio else None,
                "fecha_fin": fecha_fin.isoformat() if fecha_fin else None
            },
            "total_movimientos": len(movimientos),
            "entradas": {
                "count": len(entradas),
                "cantidad_total": sum(m.cantidad for m in entradas)
            },
            "salidas": {
                "count": len(salidas),
                "cantidad_total": sum(m.cantidad for m in salidas)
            },
            "balance": sum(m.cantidad for m in entradas) - sum(m.cantidad for m in salidas)
        }
    
    def get_reporte_movimientos(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        almacen_id: Optional[int] = None,
        tipo_movimiento: Optional[TipoMovimientoEnum] = None
    ) -> Dict[str, Any]:
        """Obtener reporte detallado de movimientos"""
        query = self.db.query(Movimiento).filter(
            Movimiento.fecha_movimiento >= fecha_inicio,
            Movimiento.fecha_movimiento <= fecha_fin
        )
        
        if almacen_id:
            query = query.filter(
                or_(
                    Movimiento.almacen_origen_id == almacen_id,
                    Movimiento.almacen_destino_id == almacen_id
                )
            )
        
        if tipo_movimiento:
            query = query.filter(Movimiento.tipo_movimiento == tipo_movimiento)
        
        movimientos = query.all()
        
        # Agrupar por tipo de movimiento
        reporte = {
            "periodo": {
                "fecha_inicio": fecha_inicio.isoformat(),
                "fecha_fin": fecha_fin.isoformat()
            },
            "filtros": {
                "almacen_id": almacen_id,
                "tipo_movimiento": tipo_movimiento.value if tipo_movimiento else None
            },
            "resumen": {
                "total_movimientos": len(movimientos),
                "por_tipo": {},
                "por_estado": {}
            },
            "movimientos": []
        }
        
        # Contar por tipo
        for tipo in TipoMovimientoEnum:
            count = len([m for m in movimientos if m.tipo_movimiento == tipo.value])
            if count > 0:
                reporte["resumen"]["por_tipo"][tipo.value] = count
        
        # Contar por estado
        for estado in EstadoMovimientoEnum:
            count = len([m for m in movimientos if m.estado == estado.value])
            if count > 0:
                reporte["resumen"]["por_estado"][estado.value] = count
        
        # Agregar lista de movimientos
        for mov in movimientos[-50:]:  # Últimos 50 movimientos
            reporte["movimientos"].append({
                "id": mov.id,
                "fecha": mov.fecha_movimiento.isoformat(),
                "tipo": mov.tipo_movimiento,
                "producto_id": mov.producto_id,
                "cantidad": float(mov.cantidad),
                "almacen_origen_id": mov.almacen_origen_id,
                "almacen_destino_id": mov.almacen_destino_id,
                "estado": mov.estado,
                "motivo": mov.motivo
            })
        
        return reporte
