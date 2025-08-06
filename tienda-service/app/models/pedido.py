# ============================================================================
# pedido.py
#
# Modelos SQLAlchemy para las entidades Pedido y PedidoDetalle. Gestiona
# el ciclo de vida completo de pedidos incluyendo estados, cálculos de
# totales y relaciones con clientes y productos.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, func, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Pedido(Base):
    """Modelo para la tabla pedidos"""
    
    __tablename__ = "pedidos"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_pedido = Column(String(50), nullable=False, unique=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    fecha_pedido = Column(DateTime, server_default=func.current_timestamp())
    fecha_requerida = Column(Date, nullable=True)
    fecha_prometida = Column(Date, nullable=True)
    fecha_entrega = Column(DateTime, nullable=True)
    estado = Column(String(50), nullable=False, default="borrador", index=True)
    subtotal = Column(Numeric(12, 2), nullable=True, default=0)
    descuento = Column(Numeric(12, 2), nullable=True, default=0)
    impuestos = Column(Numeric(12, 2), nullable=True, default=0)
    total = Column(Numeric(12, 2), nullable=True, default=0)
    metodo_pago = Column(String(50), nullable=True)
    almacen_origen_id = Column(Integer, nullable=True)
    direccion_entrega = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)
    prioridad = Column(String(20), nullable=True, default="normal", index=True)
    usuario_creacion = Column(String(255), nullable=True)
    usuario_aprobacion = Column(String(255), nullable=True)
    fecha_aprobacion = Column(DateTime, nullable=True)
    motivo_cancelacion = Column(Text, nullable=True)
    
    cliente = relationship("Cliente", back_populates="pedidos")
    detalles = relationship("PedidoDetalle", back_populates="pedido", cascade="all, delete-orphan")
    envios = relationship("Envio", back_populates="pedido")
    devoluciones = relationship("Devolucion", back_populates="pedido")
    reservas_stock = relationship("ReservaStock", back_populates="pedido")
    
    def __repr__(self):
        return f"<Pedido(id={self.id}, numero='{self.numero_pedido}', estado='{self.estado}')>"

class PedidoDetalle(Base):
    """Modelo para la tabla pedido_detalles"""
    
    __tablename__ = "pedido_detalles"
    
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id", ondelete="CASCADE"), nullable=False)
    producto_id = Column(Integer, nullable=False)
    cantidad = Column(Numeric(10, 2), nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    descuento_linea = Column(Numeric(10, 2), nullable=True, default=0)
    subtotal_linea = Column(Numeric(12, 2), nullable=False)
    
    pedido = relationship("Pedido", back_populates="detalles")
    
    def __repr__(self):
        return f"<PedidoDetalle(id={self.id}, producto_id={self.producto_id}, cantidad={self.cantidad})>"
