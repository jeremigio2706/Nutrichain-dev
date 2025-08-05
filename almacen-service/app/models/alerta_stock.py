"""
Modelo SQLAlchemy para la tabla alertas_stock
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from ..database import Base

class AlertaStock(Base):
    """Modelo para la tabla alertas_stock"""
    
    __tablename__ = "alertas_stock"
    
    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, nullable=False, index=True)
    almacen_id = Column(Integer, ForeignKey("almacenes.id"), nullable=False, index=True)
    tipo_alerta = Column(String(50), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    nivel_urgencia = Column(String(20), nullable=True, default="medio")
    leida = Column(Boolean, default=False, index=True)
    fecha_alerta = Column(DateTime, server_default=func.current_timestamp())
    fecha_resolucion = Column(DateTime, nullable=True)
    
    # Relaciones
    almacen = relationship("Almacen", back_populates="alertas")
    
    def __repr__(self):
        return f"<AlertaStock(id={self.id}, tipo='{self.tipo_alerta}', producto_id={self.producto_id}, urgencia='{self.nivel_urgencia}')>"
    
    @property
    def esta_activa(self):
        """Indica si la alerta está activa (no resuelta)"""
        return self.fecha_resolucion is None
