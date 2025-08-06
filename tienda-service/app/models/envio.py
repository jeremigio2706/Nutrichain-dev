# ============================================================================
# envio.py
#
# Modelo SQLAlchemy para la entidad Envío. Gestiona la información de
# logística y transporte de pedidos, incluyendo transportistas, vehículos
# y seguimiento de entregas.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from sqlalchemy import Column, Integer, String, DateTime, Numeric, func, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Envio(Base):
    """Modelo para la tabla envios"""
    
    __tablename__ = "envios"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_envio = Column(String(50), nullable=False, unique=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False, index=True)
    transportista = Column(String(255), nullable=True)
    vehiculo = Column(String(100), nullable=True)
    conductor = Column(String(255), nullable=True)
    telefono_conductor = Column(String(50), nullable=True)
    fecha_programada = Column(DateTime, nullable=True)
    fecha_salida = Column(DateTime, nullable=True)
    fecha_entrega = Column(DateTime, nullable=True)
    estado = Column(String(50), nullable=True, default="programado", index=True)
    observaciones = Column(Text, nullable=True)
    costo_envio = Column(Numeric(10, 2), nullable=True)
    
    pedido = relationship("Pedido", back_populates="envios")
    devoluciones = relationship("Devolucion", back_populates="envio")
    
    def __repr__(self):
        return f"<Envio(id={self.id}, numero='{self.numero_envio}', estado='{self.estado}')>"
