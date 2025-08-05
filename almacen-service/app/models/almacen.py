"""
Modelo SQLAlchemy para la tabla almacenes
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, func, Text
from sqlalchemy.orm import relationship
from ..database import Base

class Almacen(Base):
    """Modelo para la tabla almacenes"""
    
    __tablename__ = "almacenes"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    codigo = Column(String(50), nullable=False, unique=True, index=True)
    ubicacion = Column(Text, nullable=True)
    responsable = Column(String(255), nullable=True)
    telefono = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    tipo = Column(String(50), nullable=True, default="general")
    capacidad_maxima = Column(Numeric(12, 2), nullable=True)
    activo = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Relaciones
    stocks = relationship("Stock", back_populates="almacen")
    movimientos_origen = relationship("Movimiento", foreign_keys="Movimiento.almacen_origen_id", back_populates="almacen_origen")
    movimientos_destino = relationship("Movimiento", foreign_keys="Movimiento.almacen_destino_id", back_populates="almacen_destino")
    alertas = relationship("AlertaStock", back_populates="almacen")
    
    def __repr__(self):
        return f"<Almacen(id={self.id}, codigo='{self.codigo}', nombre='{self.nombre}')>"
