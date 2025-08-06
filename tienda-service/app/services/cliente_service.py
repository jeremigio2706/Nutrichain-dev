# ============================================================================
# cliente_service.py
#
# Servicio de lógica de negocio para clientes. Implementa las reglas de
# negocio relacionadas con la gestión de clientes incluyendo validaciones
# de crédito, descuentos y activación de cuentas.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from typing import List, Optional
from sqlalchemy.orm import Session

from ..repositories.cliente_repository import ClienteRepository
from ..dtos.cliente_dto import ClienteCreateDTO, ClienteUpdateDTO, ClienteResponseDTO, ClienteListResponseDTO
from ..exceptions.api_exceptions import ClienteNotFoundError, CodigoClienteExisteError, ClienteInactivoError
from ..models.cliente import Cliente

class ClienteService:
    """Servicio para lógica de negocio de clientes"""
    
    def __init__(self, db: Session):
        self.db = db
        self.cliente_repo = ClienteRepository(db)
    
    def crear_cliente(self, cliente_data: ClienteCreateDTO) -> ClienteResponseDTO:
        """Crear un nuevo cliente"""
        if self.cliente_repo.exists_codigo(cliente_data.codigo_cliente):
            raise CodigoClienteExisteError(cliente_data.codigo_cliente)
        
        cliente = self.cliente_repo.create(cliente_data)
        return ClienteResponseDTO.from_orm(cliente)
    
    def obtener_cliente(self, cliente_id: int) -> ClienteResponseDTO:
        """Obtener un cliente por ID"""
        cliente = self.cliente_repo.get_by_id(cliente_id)
        if not cliente:
            raise ClienteNotFoundError(cliente_id)
        
        return ClienteResponseDTO.from_orm(cliente)
    
    def obtener_cliente_por_codigo(self, codigo_cliente: str) -> ClienteResponseDTO:
        """Obtener un cliente por código"""
        cliente = self.cliente_repo.get_by_codigo(codigo_cliente)
        if not cliente:
            raise ClienteNotFoundError(f"Código: {codigo_cliente}")
        
        return ClienteResponseDTO.from_orm(cliente)
    
    def listar_clientes(self, page: int = 1, page_size: int = 100, activo: Optional[bool] = None) -> ClienteListResponseDTO:
        """Listar clientes con paginación"""
        skip = (page - 1) * page_size
        clientes = self.cliente_repo.get_all(skip=skip, limit=page_size, activo=activo)
        total = self.cliente_repo.count(activo=activo)
        
        clientes_dto = [ClienteResponseDTO.from_orm(cliente) for cliente in clientes]
        
        return ClienteListResponseDTO(
            clientes=clientes_dto,
            total=total,
            page=page,
            page_size=page_size
        )
    
    def actualizar_cliente(self, cliente_id: int, cliente_data: ClienteUpdateDTO) -> ClienteResponseDTO:
        """Actualizar un cliente"""
        if not self.cliente_repo.get_by_id(cliente_id):
            raise ClienteNotFoundError(cliente_id)
        
        if cliente_data.codigo_cliente and self.cliente_repo.exists_codigo(cliente_data.codigo_cliente, exclude_id=cliente_id):
            raise CodigoClienteExisteError(cliente_data.codigo_cliente)
        
        cliente = self.cliente_repo.update(cliente_id, cliente_data)
        return ClienteResponseDTO.from_orm(cliente)
    
    def desactivar_cliente(self, cliente_id: int) -> bool:
        """Desactivar un cliente"""
        if not self.cliente_repo.get_by_id(cliente_id):
            raise ClienteNotFoundError(cliente_id)
        
        return self.cliente_repo.delete(cliente_id)
    
    def buscar_clientes(self, term: str, page: int = 1, page_size: int = 100) -> ClienteListResponseDTO:
        """Buscar clientes por término"""
        skip = (page - 1) * page_size
        clientes = self.cliente_repo.search(term, skip=skip, limit=page_size)
        
        clientes_dto = [ClienteResponseDTO.from_orm(cliente) for cliente in clientes]
        
        return ClienteListResponseDTO(
            clientes=clientes_dto,
            total=len(clientes_dto),
            page=page,
            page_size=page_size
        )
    
    def validar_cliente_activo(self, cliente_id: int) -> Cliente:
        """Validar que un cliente existe y está activo"""
        cliente = self.cliente_repo.get_by_id(cliente_id)
        if not cliente:
            raise ClienteNotFoundError(cliente_id)
        
        if not cliente.activo:
            raise ClienteInactivoError(cliente_id)
        
        return cliente
    
    def validar_limite_credito(self, cliente_id: int, monto: float) -> bool:
        """Validar si el cliente puede realizar una compra basado en su límite de crédito"""
        cliente = self.validar_cliente_activo(cliente_id)
        
        if cliente.limite_credito <= 0:
            return True
        
        return monto <= float(cliente.limite_credito)
