# ============================================================================
# cliente.py
#
# Modelo SQLAlchemy para la entidad Cliente. Define la estructura de datos
# para clientes del sistema, incluyendo información personal, comercial y
# configuraciones de crédito y descuentos.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, func, Text
from sqlalchemy.orm import relationship
from ..database import Base

class Cliente(Base):
    """Modelo para la tabla clientes"""
    
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo_cliente = Column(String(50), nullable=False, unique=True, index=True)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    telefono = Column(String(50), nullable=True)
    direccion = Column(Text, nullable=True)
    ciudad = Column(String(100), nullable=True)
    pais = Column(String(50), nullable=True, default="Colombia")
    tipo_cliente = Column(String(50), nullable=True, default="minorista")
    limite_credito = Column(Numeric(12, 2), nullable=True, default=0)
    descuento_porcentaje = Column(Numeric(5, 2), nullable=True, default=0)
    activo = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp())
    
    pedidos = relationship("Pedido", back_populates="cliente")
    
    def __repr__(self):
        return f"<Cliente(id={self.id}, codigo='{self.codigo_cliente}', nombre='{self.nombre}')>"
