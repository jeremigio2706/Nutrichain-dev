# ============================================================================
# cliente_repository.py
#
# Repositorio para operaciones de base de datos relacionadas con clientes.
# Implementa el patrón Repository para abstraer el acceso a datos y 
# proporcionar operaciones CRUD optimizadas para la entidad Cliente.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.cliente import Cliente
from ..dtos.cliente_dto import ClienteCreateDTO, ClienteUpdateDTO

class ClienteRepository:
    """Repositorio para operaciones de clientes"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, cliente_data: ClienteCreateDTO) -> Cliente:
        """Crear un nuevo cliente"""
        cliente = Cliente(**cliente_data.dict())
        self.db.add(cliente)
        self.db.commit()
        self.db.refresh(cliente)
        return cliente
    
    def get_by_id(self, cliente_id: int) -> Optional[Cliente]:
        """Obtener cliente por ID"""
        return self.db.query(Cliente).filter(Cliente.id == cliente_id).first()
    
    def get_by_codigo(self, codigo_cliente: str) -> Optional[Cliente]:
        """Obtener cliente por código"""
        return self.db.query(Cliente).filter(Cliente.codigo_cliente == codigo_cliente).first()
    
    def get_by_email(self, email: str) -> Optional[Cliente]:
        """Obtener cliente por email"""
        return self.db.query(Cliente).filter(Cliente.email == email).first()
    
    def get_all(self, skip: int = 0, limit: int = 100, activo: Optional[bool] = None) -> List[Cliente]:
        """Obtener todos los clientes con paginación"""
        query = self.db.query(Cliente)
        
        if activo is not None:
            query = query.filter(Cliente.activo == activo)
        
        return query.offset(skip).limit(limit).all()
    
    def count(self, activo: Optional[bool] = None) -> int:
        """Contar clientes"""
        query = self.db.query(func.count(Cliente.id))
        
        if activo is not None:
            query = query.filter(Cliente.activo == activo)
        
        return query.scalar()
    
    def update(self, cliente_id: int, cliente_data: ClienteUpdateDTO) -> Optional[Cliente]:
        """Actualizar un cliente"""
        cliente = self.get_by_id(cliente_id)
        if not cliente:
            return None
        
        update_data = cliente_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(cliente, field, value)
        
        cliente.updated_at = func.current_timestamp()
        self.db.commit()
        self.db.refresh(cliente)
        return cliente
    
    def delete(self, cliente_id: int) -> bool:
        """Eliminar un cliente (soft delete)"""
        cliente = self.get_by_id(cliente_id)
        if not cliente:
            return False
        
        cliente.activo = False
        cliente.updated_at = func.current_timestamp()
        self.db.commit()
        return True
    
    def search(self, term: str, skip: int = 0, limit: int = 100) -> List[Cliente]:
        """Buscar clientes por término"""
        query = self.db.query(Cliente).filter(
            (Cliente.nombre.ilike(f"%{term}%")) |
            (Cliente.codigo_cliente.ilike(f"%{term}%")) |
            (Cliente.email.ilike(f"%{term}%"))
        )
        return query.offset(skip).limit(limit).all()
    
    def exists_codigo(self, codigo_cliente: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si existe un código de cliente"""
        query = self.db.query(Cliente).filter(Cliente.codigo_cliente == codigo_cliente)
        
        if exclude_id:
            query = query.filter(Cliente.id != exclude_id)
        
        return query.first() is not None
