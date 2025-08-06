# ============================================================================
# pedido_repository.py
#
# Repositorio para operaciones de base de datos relacionadas con pedidos.
# Maneja las operaciones CRUD complejas incluyendo detalles de pedido,
# cálculos de totales y gestión de estados del ciclo de vida.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from decimal import Decimal

from ..models.pedido import Pedido, PedidoDetalle
from ..models.reserva_stock import ReservaStock
from ..dtos.pedido_dto import PedidoCreateDTO, PedidoUpdateDTO

class PedidoRepository:
    """Repositorio para operaciones de pedidos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, pedido_data: PedidoCreateDTO, numero_pedido: str, usuario_creacion: str) -> Pedido:
        """Crear un nuevo pedido con sus detalles"""
        pedido = Pedido(
            numero_pedido=numero_pedido,
            cliente_id=pedido_data.cliente_id,
            fecha_requerida=pedido_data.fecha_requerida,
            fecha_prometida=pedido_data.fecha_prometida,
            metodo_pago=pedido_data.metodo_pago,
            almacen_origen_id=pedido_data.almacen_origen_id,
            direccion_entrega=pedido_data.direccion_entrega,
            observaciones=pedido_data.observaciones,
            prioridad=pedido_data.prioridad,
            usuario_creacion=usuario_creacion,
            estado="borrador"
        )
        
        self.db.add(pedido)
        self.db.flush()
        
        subtotal = Decimal('0')
        for detalle_data in pedido_data.detalles:
            subtotal_linea = detalle_data.cantidad * detalle_data.precio_unitario - detalle_data.descuento_linea
            
            detalle = PedidoDetalle(
                pedido_id=pedido.id,
                producto_id=detalle_data.producto_id,
                cantidad=detalle_data.cantidad,
                precio_unitario=detalle_data.precio_unitario,
                descuento_linea=detalle_data.descuento_linea,
                subtotal_linea=subtotal_linea
            )
            self.db.add(detalle)
            subtotal += subtotal_linea
        
        pedido.subtotal = subtotal
        pedido.total = subtotal
        
        self.db.commit()
        self.db.refresh(pedido)
        return pedido
    
    def get_by_id(self, pedido_id: int) -> Optional[Pedido]:
        """Obtener pedido por ID con sus detalles"""
        return (self.db.query(Pedido)
                .options(joinedload(Pedido.detalles), joinedload(Pedido.cliente))
                .filter(Pedido.id == pedido_id)
                .first())
    
    def get_by_numero(self, numero_pedido: str) -> Optional[Pedido]:
        """Obtener pedido por número"""
        return (self.db.query(Pedido)
                .options(joinedload(Pedido.detalles))
                .filter(Pedido.numero_pedido == numero_pedido)
                .first())
    
    def get_all(self, skip: int = 0, limit: int = 100, cliente_id: Optional[int] = None, 
                estado: Optional[str] = None) -> List[Pedido]:
        """Obtener todos los pedidos con filtros"""
        query = (self.db.query(Pedido)
                .options(joinedload(Pedido.detalles), joinedload(Pedido.cliente))
                .order_by(desc(Pedido.fecha_pedido)))
        
        if cliente_id:
            query = query.filter(Pedido.cliente_id == cliente_id)
        
        if estado:
            query = query.filter(Pedido.estado == estado)
        
        return query.offset(skip).limit(limit).all()
    
    def count(self, cliente_id: Optional[int] = None, estado: Optional[str] = None) -> int:
        """Contar pedidos"""
        query = self.db.query(func.count(Pedido.id))
        
        if cliente_id:
            query = query.filter(Pedido.cliente_id == cliente_id)
        
        if estado:
            query = query.filter(Pedido.estado == estado)
        
        return query.scalar()
    
    def update(self, pedido_id: int, pedido_data: PedidoUpdateDTO) -> Optional[Pedido]:
        """Actualizar un pedido"""
        pedido = self.get_by_id(pedido_id)
        if not pedido:
            return None
        
        update_data = pedido_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(pedido, field, value)
        
        self.db.commit()
        self.db.refresh(pedido)
        return pedido
    
    def update_estado(self, pedido_id: int, nuevo_estado: str, usuario: Optional[str] = None) -> Optional[Pedido]:
        """Actualizar estado del pedido"""
        pedido = self.get_by_id(pedido_id)
        if not pedido:
            return None
        
        pedido.estado = nuevo_estado
        
        if nuevo_estado == "confirmado" and usuario:
            pedido.usuario_aprobacion = usuario
            pedido.fecha_aprobacion = func.current_timestamp()
        
        self.db.commit()
        self.db.refresh(pedido)
        return pedido
    
    def get_detalles_by_producto(self, producto_id: int) -> List[PedidoDetalle]:
        """Obtener detalles de pedido por producto"""
        return (self.db.query(PedidoDetalle)
                .options(joinedload(PedidoDetalle.pedido))
                .filter(PedidoDetalle.producto_id == producto_id)
                .all())
    
    def exists_numero(self, numero_pedido: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe un número de pedido"""
        query = self.db.query(Pedido).filter(Pedido.numero_pedido == numero_pedido)
        
        if exclude_id:
            query = query.filter(Pedido.id != exclude_id)
        
        return query.first() is not None
    
    def get_next_numero(self, prefix: str = "PED") -> str:
        """Generar el siguiente número de pedido"""
        last_pedido = (self.db.query(Pedido)
                      .filter(Pedido.numero_pedido.like(f"{prefix}%"))
                      .order_by(desc(Pedido.id))
                      .first())
        
        if not last_pedido:
            return f"{prefix}000001"
        
        try:
            last_number = int(last_pedido.numero_pedido.replace(prefix, ""))
            next_number = last_number + 1
            return f"{prefix}{next_number:06d}"
        except ValueError:
            return f"{prefix}000001"

class ReservaStockRepository:
    """Repositorio para operaciones de reserva de stock"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_reserva(self, pedido_id: int, producto_id: int, cantidad: Decimal, almacen_id: int) -> ReservaStock:
        """Crear una reserva de stock"""
        reserva = ReservaStock(
            pedido_id=pedido_id,
            producto_id=producto_id,
            cantidad_reservada=cantidad,
            almacen_id=almacen_id
        )
        self.db.add(reserva)
        self.db.commit()
        self.db.refresh(reserva)
        return reserva
    
    def get_by_pedido(self, pedido_id: int) -> List[ReservaStock]:
        """Obtener reservas por pedido"""
        return self.db.query(ReservaStock).filter(ReservaStock.pedido_id == pedido_id).all()
    
    def liberar_reservas(self, pedido_id: int) -> bool:
        """Liberar reservas de un pedido"""
        reservas = self.get_by_pedido(pedido_id)
        for reserva in reservas:
            reserva.activa = False
        
        self.db.commit()
        return True
    
    def delete_reservas(self, pedido_id: int) -> bool:
        """Eliminar reservas de un pedido"""
        self.db.query(ReservaStock).filter(ReservaStock.pedido_id == pedido_id).delete()
        self.db.commit()
        return True
