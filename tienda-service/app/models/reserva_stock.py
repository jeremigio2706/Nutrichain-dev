# ============================================================================
# reserva_stock.py
#
# Modelo SQLAlchemy para la entidad ReservaStock. Gestiona las reservas
# temporales de productos para evitar sobreventa durante el proceso de
# confirmación de pedidos.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from sqlalchemy import Column, Integer, DateTime, Numeric, func, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ..database import Base

class ReservaStock(Base):
    """Modelo para la tabla reservas_stock"""
    
    __tablename__ = "reservas_stock"
    
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    producto_id = Column(Integer, nullable=False)
    cantidad_reservada = Column(Numeric(10, 2), nullable=False)
    almacen_id = Column(Integer, nullable=False)
    fecha_reserva = Column(DateTime, server_default=func.current_timestamp())
    fecha_expiracion = Column(DateTime, nullable=True)
    activa = Column(Boolean, default=True)
    
    pedido = relationship("Pedido", back_populates="reservas_stock")
    
    def __repr__(self):
        return f"<ReservaStock(id={self.id}, pedido_id={self.pedido_id}, producto_id={self.producto_id})>"
