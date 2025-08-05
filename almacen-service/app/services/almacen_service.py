"""
Servicios para la lógica de negocio del almacén
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from decimal import Decimal

from ..models import Almacen, Stock, Movimiento
from ..exceptions.api_exceptions import NotFoundError, ValidationError, BusinessLogicError
from ..dtos.almacen_dto import (
    AlmacenCreateDTO as AlmacenCreate, 
    AlmacenUpdateDTO as AlmacenUpdate, 
    AlmacenResponseDTO as AlmacenResponse,
    AlmacenEstadisticasDTO as AlmacenEstadisticas
)
from ..dtos.stock_dto import StockResponseDTO as StockResponse
from ..dtos.movimiento_dto import MovimientoResponseDTO as MovimientoResponse
from ..database import get_db

class AlmacenService:
    """Servicio para gestión de almacenes"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def crear_almacen(self, almacen_data: AlmacenCreate) -> AlmacenResponse:
        """Crear nuevo almacén"""
        # Verificar que no exista un almacén con el mismo nombre
        existing = self.db.query(Almacen).filter(
            Almacen.nombre == almacen_data.nombre
        ).first()
        
        if existing:
            raise ValueError(f"Ya existe un almacén con el nombre '{almacen_data.nombre}'")
        
        # Crear nuevo almacén
        almacen = Almacen(**almacen_data.dict())
        
        try:
            self.db.add(almacen)
            self.db.commit()
            self.db.refresh(almacen)
            
            return AlmacenResponse.from_orm(almacen)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Error al crear el almacén")
    
    def obtener_almacen(self, almacen_id: int) -> AlmacenResponse:
        """Obtener almacén por ID"""
        almacen = self.db.query(Almacen).filter(Almacen.id == almacen_id).first()
        
        if not almacen:
            raise NotFoundError(f"Almacén con ID {almacen_id} no encontrado")
        
        return AlmacenResponse.from_orm(almacen)
    
    def obtener_almacenes(
        self, 
        skip: int = 0, 
        limit: int = 100,
        activo: Optional[bool] = None
    ) -> List[AlmacenResponse]:
        """Obtener lista de almacenes"""
        query = self.db.query(Almacen)
        
        if activo is not None:
            query = query.filter(Almacen.activo == activo)
        
        almacenes = query.offset(skip).limit(limit).all()
        
        return [AlmacenResponse.from_orm(almacen) for almacen in almacenes]
    
    def listar_almacenes(
        self, 
        activo: Optional[bool] = None,
        tipo: Optional[str] = None,
        ubicacion: Optional[str] = None,
        limit: Optional[int] = 100,
        offset: int = 0
    ):
        """Listar almacenes con filtros opcionales"""
        from ..dtos.almacen_dto import AlmacenListDTO as AlmacenList
        
        query = self.db.query(Almacen)
        
        # Aplicar filtros
        if activo is not None:
            query = query.filter(Almacen.activo == activo)
        if ubicacion:
            query = query.filter(Almacen.direccion.ilike(f"%{ubicacion}%"))
        
        # Obtener total de registros sin paginación
        total = query.count()
        
        # Aplicar paginación solo si limit no es None
        if limit is not None:
            almacenes = query.offset(offset).limit(limit).all()
        else:
            almacenes = query.all()
        
        # Convertir a responses
        almacenes_response = [AlmacenResponse.from_orm(almacen) for almacen in almacenes]
        
        return AlmacenList(
            almacenes=almacenes_response,
            total=total,
            offset=offset,
            limit=limit
        )
    
    def actualizar_almacen(
        self, 
        almacen_id: int, 
        almacen_data: AlmacenUpdate
    ) -> Optional[AlmacenResponse]:
        """Actualizar almacén"""
        almacen = self.db.query(Almacen).filter(Almacen.id == almacen_id).first()
        
        if not almacen:
            return None
        
        # Verificar nombre único si se está actualizando
        if almacen_data.nombre and almacen_data.nombre != almacen.nombre:
            existing = self.db.query(Almacen).filter(
                Almacen.nombre == almacen_data.nombre,
                Almacen.id != almacen_id
            ).first()
            
            if existing:
                raise ValueError(f"Ya existe un almacén con el nombre '{almacen_data.nombre}'")
        
        # Actualizar campos
        update_data = almacen_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(almacen, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(almacen)
            
            return AlmacenResponse.from_orm(almacen)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Error al actualizar el almacén")
    
    def eliminar_almacen(self, almacen_id: int) -> bool:
        """Eliminar almacén (soft delete)"""
        almacen = self.db.query(Almacen).filter(Almacen.id == almacen_id).first()
        
        if not almacen:
            return False
        
        # Verificar que no tenga stock activo
        stock_activo = self.db.query(Stock).filter(
            Stock.almacen_id == almacen_id,
            Stock.cantidad_actual > 0
        ).first()
        
        if stock_activo:
            raise ValueError("No se puede eliminar un almacén con stock activo")
        
        # Soft delete
        almacen.activo = False
        
        try:
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            return False
    
    def obtener_estadisticas(self, almacen_id: int) -> Optional[AlmacenEstadisticas]:
        """Obtener estadísticas del almacén"""
        almacen = self.db.query(Almacen).filter(Almacen.id == almacen_id).first()
        
        if not almacen:
            return None
        
        # Consultar stocks
        stocks = self.db.query(Stock).filter(Stock.almacen_id == almacen_id).all()
        
        total_productos = len(stocks)
        total_stock = sum(stock.cantidad_actual for stock in stocks)
        valor_inventario = sum(
            stock.cantidad_actual * (stock.costo_unitario or Decimal('0'))
            for stock in stocks
        )
        
        # Productos con bajo stock
        productos_bajo_stock = sum(
            1 for stock in stocks 
            if stock.cantidad_minima and stock.cantidad_actual <= stock.cantidad_minima
        )
        
        # Productos sin stock
        productos_sin_stock = sum(
            1 for stock in stocks 
            if stock.cantidad_actual <= 0
        )
        
        # Movimientos del mes actual
        inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        movimientos_mes = self.db.query(Movimiento).filter(
            (Movimiento.almacen_origen_id == almacen_id) |
            (Movimiento.almacen_destino_id == almacen_id),
            Movimiento.fecha_movimiento >= inicio_mes
        ).count()
        
        # Último movimiento
        ultimo_mov = self.db.query(Movimiento).filter(
            (Movimiento.almacen_origen_id == almacen_id) |
            (Movimiento.almacen_destino_id == almacen_id)
        ).order_by(Movimiento.fecha_movimiento.desc()).first()
        
        ultimo_movimiento = None
        if ultimo_mov:
            ultimo_movimiento = ultimo_mov.fecha_movimiento
        
        return AlmacenEstadisticas(
            almacen_id=almacen.id,
            almacen_nombre=almacen.nombre,
            almacen_codigo=almacen.codigo,
            total_productos=total_productos,
            total_stock=total_stock,
            valor_inventario=valor_inventario,
            productos_bajo_stock=productos_bajo_stock,
            productos_sin_stock=productos_sin_stock,
            alertas_activas=productos_bajo_stock + productos_sin_stock,  # Calculamos alertas como suma de bajo stock y sin stock
            movimientos_mes=movimientos_mes,
            ultimo_movimiento=ultimo_movimiento
        )
    
    def verificar_disponibilidad(self, almacen_id: int) -> bool:
        """Verificar si el almacén está disponible"""
        almacen = self.db.query(Almacen).filter(
            Almacen.id == almacen_id,
            Almacen.activo == True
        ).first()
        
        return almacen is not None
