# ============================================================================
# envio_repository.py
#
# Repositorio para operaciones de base de datos relacionadas con envíos.
# Gestiona las operaciones CRUD para envíos incluyendo generación de 
# números únicos y seguimiento de estados de entrega.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc

from ..models.envio import Envio
from ..dtos.envio_dto import EnvioCreateDTO, EnvioUpdateDTO

class EnvioRepository:
    """Repositorio para operaciones de envíos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, envio_data: EnvioCreateDTO, numero_envio: str) -> Envio:
        """Crear un nuevo envío"""
        envio = Envio(
            numero_envio=numero_envio,
            pedido_id=envio_data.pedido_id,
            transportista=envio_data.transportista,
            vehiculo=envio_data.vehiculo,
            conductor=envio_data.conductor,
            telefono_conductor=envio_data.telefono_conductor,
            fecha_programada=envio_data.fecha_programada,
            observaciones=envio_data.observaciones,
            costo_envio=envio_data.costo_envio,
            estado="programado"
        )
        
        self.db.add(envio)
        self.db.commit()
        self.db.refresh(envio)
        return envio
    
    def get_by_id(self, envio_id: int) -> Optional[Envio]:
        """Obtener envío por ID"""
        return (self.db.query(Envio)
                .options(joinedload(Envio.pedido))
                .filter(Envio.id == envio_id)
                .first())
    
    def get_by_numero(self, numero_envio: str) -> Optional[Envio]:
        """Obtener envío por número"""
        return self.db.query(Envio).filter(Envio.numero_envio == numero_envio).first()
    
    def get_by_pedido(self, pedido_id: int) -> List[Envio]:
        """Obtener envíos por pedido"""
        return (self.db.query(Envio)
                .filter(Envio.pedido_id == pedido_id)
                .order_by(desc(Envio.fecha_programada))
                .all())
    
    def get_all(self, skip: int = 0, limit: int = 100, estado: Optional[str] = None) -> List[Envio]:
        """Obtener todos los envíos con filtros"""
        query = (self.db.query(Envio)
                .options(joinedload(Envio.pedido))
                .order_by(desc(Envio.fecha_programada)))
        
        if estado:
            query = query.filter(Envio.estado == estado)
        
        return query.offset(skip).limit(limit).all()
    
    def count(self, estado: Optional[str] = None) -> int:
        """Contar envíos"""
        query = self.db.query(func.count(Envio.id))
        
        if estado:
            query = query.filter(Envio.estado == estado)
        
        return query.scalar()
    
    def update(self, envio_id: int, envio_data: EnvioUpdateDTO) -> Optional[Envio]:
        """Actualizar un envío"""
        envio = self.get_by_id(envio_id)
        if not envio:
            return None
        
        update_data = envio_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(envio, field, value)
        
        self.db.commit()
        self.db.refresh(envio)
        return envio
    
    def update_estado(self, envio_id: int, nuevo_estado: str) -> Optional[Envio]:
        """Actualizar estado del envío"""
        envio = self.get_by_id(envio_id)
        if not envio:
            return None
        
        envio.estado = nuevo_estado
        
        if nuevo_estado == "en_transito" and not envio.fecha_salida:
            envio.fecha_salida = func.current_timestamp()
        elif nuevo_estado == "entregado" and not envio.fecha_entrega:
            envio.fecha_entrega = func.current_timestamp()
        
        self.db.commit()
        self.db.refresh(envio)
        return envio
    
    def exists_numero(self, numero_envio: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe un número de envío"""
        query = self.db.query(Envio).filter(Envio.numero_envio == numero_envio)
        
        if exclude_id:
            query = query.filter(Envio.id != exclude_id)
        
        return query.first() is not None
    
    def get_next_numero(self, prefix: str = "ENV") -> str:
        """Generar el siguiente número de envío"""
        last_envio = (self.db.query(Envio)
                     .filter(Envio.numero_envio.like(f"{prefix}%"))
                     .order_by(desc(Envio.id))
                     .first())
        
        if not last_envio:
            return f"{prefix}000001"
        
        try:
            last_number = int(last_envio.numero_envio.replace(prefix, ""))
            next_number = last_number + 1
            return f"{prefix}{next_number:06d}"
        except ValueError:
            return f"{prefix}000001"
