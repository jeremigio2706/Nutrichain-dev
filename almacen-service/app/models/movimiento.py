"""
Modelo SQLAlchemy para la tabla movimientos
"""

from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from ..database import Base

class Movimiento(Base):
    """Modelo para la tabla movimientos"""
    
    __tablename__ = "movimientos"
    
    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, nullable=False, index=True)
    almacen_origen_id = Column(Integer, ForeignKey("almacenes.id"), nullable=True, index=True)
    almacen_destino_id = Column(Integer, ForeignKey("almacenes.id"), nullable=True, index=True)
    tipo_movimiento = Column(String(50), nullable=False, index=True)
    cantidad = Column(Numeric(10, 2), nullable=False)
    cantidad_real = Column(Numeric(10, 2), nullable=True)
    motivo = Column(Text, nullable=True)
    referencia_externa = Column(String(255), nullable=True)
    costo_unitario = Column(Numeric(10, 2), nullable=True)
    costo_total = Column(Numeric(10, 2), nullable=True)
    fecha_movimiento = Column(DateTime, server_default=func.current_timestamp(), index=True)
    fecha_procesamiento = Column(DateTime, nullable=True)
    usuario = Column(String(255), nullable=True)
    estado = Column(String(50), nullable=True, default="pendiente", index=True)
    observaciones = Column(Text, nullable=True)
    
    # Relaciones
    almacen_origen = relationship("Almacen", foreign_keys=[almacen_origen_id], back_populates="movimientos_origen")
    almacen_destino = relationship("Almacen", foreign_keys=[almacen_destino_id], back_populates="movimientos_destino")
    
    def __repr__(self):
        return f"<Movimiento(id={self.id}, tipo='{self.tipo_movimiento}', producto_id={self.producto_id}, cantidad={self.cantidad})>"
