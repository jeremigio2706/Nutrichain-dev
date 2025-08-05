"""
Modelo SQLAlchemy para la tabla stock
"""

from sqlalchemy import Column, Integer, String, DateTime, Numeric, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from ..database import Base

class Stock(Base):
    """Modelo para la tabla stock"""
    
    __tablename__ = "stock"
    
    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, nullable=False, index=True)
    almacen_id = Column(Integer, ForeignKey("almacenes.id"), nullable=False, index=True)
    cantidad_actual = Column(Numeric(10, 2), nullable=False, default=0)
    cantidad_reservada = Column(Numeric(10, 2), nullable=False, default=0)
    cantidad_minima = Column(Numeric(10, 2), nullable=True, default=0)
    cantidad_maxima = Column(Numeric(10, 2), nullable=True)
    ubicacion_fisica = Column(String(255), nullable=True)
    lote = Column(String(100), nullable=True)
    fecha_vencimiento = Column(Date, nullable=True)
    costo_unitario = Column(Numeric(10, 2), nullable=True)
    updated_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Relaciones
    almacen = relationship("Almacen", back_populates="stocks")
    
    def __repr__(self):
        return f"<Stock(id={self.id}, producto_id={self.producto_id}, almacen_id={self.almacen_id}, cantidad={self.cantidad_actual})>"
    
    @property
    def cantidad_disponible(self):
        """Cantidad disponible para venta (actual - reservada)"""
        return self.cantidad_actual - self.cantidad_reservada
    
    @property
    def stock_bajo(self):
        """Indica si el stock está por debajo del mínimo"""
        if self.cantidad_minima:
            return self.cantidad_actual <= self.cantidad_minima
        return False
    
    @property
    def stock_agotado(self):
        """Indica si el stock está agotado"""
        return self.cantidad_disponible <= 0
