# ============================================================================
# devolucion.py
#
# Modelos SQLAlchemy para las entidades Devolución y DevolucionDetalle.
# Gestiona el proceso completo de devoluciones incluyendo motivos, estados
# y acciones a tomar con los productos devueltos.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from sqlalchemy import Column, Integer, String, DateTime, Numeric, func, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Devolucion(Base):
    """Modelo para la tabla devoluciones"""
    
    __tablename__ = "devoluciones"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_devolucion = Column(String(50), nullable=False, unique=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    envio_id = Column(Integer, ForeignKey("envios.id"), nullable=True)
    fecha_devolucion = Column(DateTime, server_default=func.current_timestamp())
    motivo = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    estado = Column(String(50), nullable=True, default="recibida")
    usuario_procesamiento = Column(String(255), nullable=True)
    fecha_procesamiento = Column(DateTime, nullable=True)
    
    pedido = relationship("Pedido", back_populates="devoluciones")
    envio = relationship("Envio", back_populates="devoluciones")
    detalles = relationship("DevolucionDetalle", back_populates="devolucion", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Devolucion(id={self.id}, numero='{self.numero_devolucion}', estado='{self.estado}')>"

class DevolucionDetalle(Base):
    """Modelo para la tabla devolucion_detalles"""
    
    __tablename__ = "devolucion_detalles"
    
    id = Column(Integer, primary_key=True, index=True)
    devolucion_id = Column(Integer, ForeignKey("devoluciones.id", ondelete="CASCADE"), nullable=False)
    producto_id = Column(Integer, nullable=False)
    cantidad_devuelta = Column(Numeric(10, 2), nullable=False)
    motivo_detalle = Column(String(100), nullable=True)
    estado_producto = Column(String(50), nullable=True)
    accion = Column(String(50), nullable=True)
    
    devolucion = relationship("Devolucion", back_populates="detalles")
    
    def __repr__(self):
        return f"<DevolucionDetalle(id={self.id}, producto_id={self.producto_id}, cantidad={self.cantidad_devuelta})>"
