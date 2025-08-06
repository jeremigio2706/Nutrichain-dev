# ============================================================================
# devolucion_repository.py
#
# Repositorio para operaciones de base de datos relacionadas con devoluciones.
# Maneja las operaciones CRUD complejas incluyendo detalles de devolución
# y gestión del proceso completo de devoluciones.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc

from ..models.devolucion import Devolucion, DevolucionDetalle
from ..dtos.devolucion_dto import DevolucionCreateDTO, DevolucionUpdateDTO

class DevolucionRepository:
    """Repositorio para operaciones de devoluciones"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, devolucion_data: DevolucionCreateDTO, numero_devolucion: str) -> Devolucion:
        """Crear una nueva devolución con sus detalles"""
        devolucion = Devolucion(
            numero_devolucion=numero_devolucion,
            pedido_id=devolucion_data.pedido_id,
            envio_id=devolucion_data.envio_id,
            motivo=devolucion_data.motivo,
            descripcion=devolucion_data.descripcion,
            estado="recibida"
        )
        
        self.db.add(devolucion)
        self.db.flush()
        
        for detalle_data in devolucion_data.detalles:
            detalle = DevolucionDetalle(
                devolucion_id=devolucion.id,
                producto_id=detalle_data.producto_id,
                cantidad_devuelta=detalle_data.cantidad_devuelta,
                motivo_detalle=detalle_data.motivo_detalle,
                estado_producto=detalle_data.estado_producto,
                accion=detalle_data.accion
            )
            self.db.add(detalle)
        
        self.db.commit()
        self.db.refresh(devolucion)
        return devolucion
    
    def get_by_id(self, devolucion_id: int) -> Optional[Devolucion]:
        """Obtener devolución por ID con sus detalles"""
        return (self.db.query(Devolucion)
                .options(joinedload(Devolucion.detalles), 
                        joinedload(Devolucion.pedido),
                        joinedload(Devolucion.envio))
                .filter(Devolucion.id == devolucion_id)
                .first())
    
    def get_by_numero(self, numero_devolucion: str) -> Optional[Devolucion]:
        """Obtener devolución por número"""
        return (self.db.query(Devolucion)
                .options(joinedload(Devolucion.detalles))
                .filter(Devolucion.numero_devolucion == numero_devolucion)
                .first())
    
    def get_by_pedido(self, pedido_id: int) -> List[Devolucion]:
        """Obtener devoluciones por pedido"""
        return (self.db.query(Devolucion)
                .options(joinedload(Devolucion.detalles))
                .filter(Devolucion.pedido_id == pedido_id)
                .order_by(desc(Devolucion.fecha_devolucion))
                .all())
    
    def get_all(self, skip: int = 0, limit: int = 100, estado: Optional[str] = None) -> List[Devolucion]:
        """Obtener todas las devoluciones con filtros"""
        query = (self.db.query(Devolucion)
                .options(joinedload(Devolucion.detalles),
                        joinedload(Devolucion.pedido))
                .order_by(desc(Devolucion.fecha_devolucion)))
        
        if estado:
            query = query.filter(Devolucion.estado == estado)
        
        return query.offset(skip).limit(limit).all()
    
    def count(self, estado: Optional[str] = None) -> int:
        """Contar devoluciones"""
        query = self.db.query(func.count(Devolucion.id))
        
        if estado:
            query = query.filter(Devolucion.estado == estado)
        
        return query.scalar()
    
    def update(self, devolucion_id: int, devolucion_data: DevolucionUpdateDTO) -> Optional[Devolucion]:
        """Actualizar una devolución"""
        devolucion = self.get_by_id(devolucion_id)
        if not devolucion:
            return None
        
        update_data = devolucion_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(devolucion, field, value)
        
        self.db.commit()
        self.db.refresh(devolucion)
        return devolucion
    
    def update_estado(self, devolucion_id: int, nuevo_estado: str, usuario: Optional[str] = None) -> Optional[Devolucion]:
        """Actualizar estado de la devolución"""
        devolucion = self.get_by_id(devolucion_id)
        if not devolucion:
            return None
        
        devolucion.estado = nuevo_estado
        
        if usuario:
            devolucion.usuario_procesamiento = usuario
            devolucion.fecha_procesamiento = func.current_timestamp()
        
        self.db.commit()
        self.db.refresh(devolucion)
        return devolucion
    
    def get_detalles_by_producto(self, producto_id: int) -> List[DevolucionDetalle]:
        """Obtener detalles de devolución por producto"""
        return (self.db.query(DevolucionDetalle)
                .options(joinedload(DevolucionDetalle.devolucion))
                .filter(DevolucionDetalle.producto_id == producto_id)
                .all())
    
    def exists_numero(self, numero_devolucion: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe un número de devolución"""
        query = self.db.query(Devolucion).filter(Devolucion.numero_devolucion == numero_devolucion)
        
        if exclude_id:
            query = query.filter(Devolucion.id != exclude_id)
        
        return query.first() is not None
    
    def get_next_numero(self, prefix: str = "DEV") -> str:
        """Generar el siguiente número de devolución"""
        last_devolucion = (self.db.query(Devolucion)
                          .filter(Devolucion.numero_devolucion.like(f"{prefix}%"))
                          .order_by(desc(Devolucion.id))
                          .first())
        
        if not last_devolucion:
            return f"{prefix}000001"
        
        try:
            last_number = int(last_devolucion.numero_devolucion.replace(prefix, ""))
            next_number = last_number + 1
            return f"{prefix}{next_number:06d}"
        except ValueError:
            return f"{prefix}000001"
