# ============================================================================
# envio_service.py
#
# Servicio de lógica de negocio para envíos. Gestiona el ciclo completo
# de envíos incluyendo programación, seguimiento y actualización de
# estados de entrega.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from typing import List, Optional
from sqlalchemy.orm import Session

from ..repositories.envio_repository import EnvioRepository
from ..repositories.pedido_repository import PedidoRepository
from ..services.external_service import ExternalService
from ..dtos.envio_dto import EnvioCreateDTO, EnvioUpdateDTO, EnvioResponseDTO, EnvioListResponseDTO
from ..exceptions.api_exceptions import EnvioNotFoundError, PedidoNotFoundError, PedidoEstadoInvalidoError
from ..config import settings

class EnvioService:
    """Servicio para lógica de negocio de envíos"""
    
    def __init__(self, db: Session):
        self.db = db
        self.envio_repo = EnvioRepository(db)
        self.pedido_repo = PedidoRepository(db)
        self.external_service = ExternalService()
    
    def crear_envio(self, envio_data: EnvioCreateDTO) -> EnvioResponseDTO:
        """Crear un nuevo envío"""
        pedido = self.pedido_repo.get_by_id(envio_data.pedido_id)
        if not pedido:
            raise PedidoNotFoundError(envio_data.pedido_id)
        
        if pedido.estado not in ["confirmado", "preparando"]:
            raise PedidoEstadoInvalidoError(
                envio_data.pedido_id, 
                pedido.estado, 
                "confirmado o preparando"
            )
        
        numero_envio = self.envio_repo.get_next_numero(settings.numero_envio_prefix)
        
        envio = self.envio_repo.create(envio_data, numero_envio)
        
        if pedido.estado == "confirmado":
            self.pedido_repo.update_estado(envio_data.pedido_id, "preparando")
        
        self.external_service.encolar_tarea_pedido(
            envio_data.pedido_id,
            "envio_creado",
            {
                "envio_id": envio.id,
                "numero_envio": numero_envio,
                "transportista": envio_data.transportista
            }
        )
        
        return EnvioResponseDTO.from_orm(envio)
    
    def obtener_envio(self, envio_id: int) -> EnvioResponseDTO:
        """Obtener un envío por ID"""
        envio = self.envio_repo.get_by_id(envio_id)
        if not envio:
            raise EnvioNotFoundError(envio_id)
        
        return EnvioResponseDTO.from_orm(envio)
    
    def obtener_envio_por_numero(self, numero_envio: str) -> EnvioResponseDTO:
        """Obtener un envío por número"""
        envio = self.envio_repo.get_by_numero(numero_envio)
        if not envio:
            raise EnvioNotFoundError(f"Número: {numero_envio}")
        
        return EnvioResponseDTO.from_orm(envio)
    
    def obtener_envios_pedido(self, pedido_id: int) -> List[EnvioResponseDTO]:
        """Obtener todos los envíos de un pedido"""
        if not self.pedido_repo.get_by_id(pedido_id):
            raise PedidoNotFoundError(pedido_id)
        
        envios = self.envio_repo.get_by_pedido(pedido_id)
        return [EnvioResponseDTO.from_orm(envio) for envio in envios]
    
    def listar_envios(self, page: int = 1, page_size: int = 100, 
                     estado: Optional[str] = None) -> EnvioListResponseDTO:
        """Listar envíos con filtros y paginación"""
        skip = (page - 1) * page_size
        envios = self.envio_repo.get_all(skip=skip, limit=page_size, estado=estado)
        total = self.envio_repo.count(estado=estado)
        
        envios_dto = [EnvioResponseDTO.from_orm(envio) for envio in envios]
        
        return EnvioListResponseDTO(
            envios=envios_dto,
            total=total,
            page=page,
            page_size=page_size
        )
    
    def actualizar_envio(self, envio_id: int, envio_data: EnvioUpdateDTO) -> EnvioResponseDTO:
        """Actualizar un envío"""
        envio = self.envio_repo.get_by_id(envio_id)
        if not envio:
            raise EnvioNotFoundError(envio_id)
        
        envio_actualizado = self.envio_repo.update(envio_id, envio_data)
        
        if envio_data.estado and envio_data.estado != envio.estado:
            self.external_service.encolar_tarea_pedido(
                envio.pedido_id,
                "envio_actualizado",
                {
                    "envio_id": envio_id,
                    "estado_anterior": envio.estado,
                    "estado_nuevo": envio_data.estado
                }
            )
        
        return EnvioResponseDTO.from_orm(envio_actualizado)
    
    def iniciar_transito(self, envio_id: int) -> EnvioResponseDTO:
        """Iniciar tránsito del envío"""
        envio = self.envio_repo.get_by_id(envio_id)
        if not envio:
            raise EnvioNotFoundError(envio_id)
        
        if envio.estado != "programado":
            raise ValueError(f"Envío debe estar en estado 'programado', actual: {envio.estado}")
        
        envio_actualizado = self.envio_repo.update_estado(envio_id, "en_transito")
        
        self.pedido_repo.update_estado(envio.pedido_id, "enviado")
        
        self.external_service.encolar_tarea_pedido(
            envio.pedido_id,
            "envio_en_transito",
            {"envio_id": envio_id, "numero_envio": envio.numero_envio}
        )
        
        return EnvioResponseDTO.from_orm(envio_actualizado)
    
    def marcar_entregado(self, envio_id: int) -> EnvioResponseDTO:
        """Marcar envío como entregado"""
        envio = self.envio_repo.get_by_id(envio_id)
        if not envio:
            raise EnvioNotFoundError(envio_id)
        
        if envio.estado != "en_transito":
            raise ValueError(f"Envío debe estar 'en_transito', actual: {envio.estado}")
        
        envio_actualizado = self.envio_repo.update_estado(envio_id, "entregado")
        
        self.pedido_repo.update_estado(envio.pedido_id, "entregado")
        
        self.external_service.encolar_tarea_pedido(
            envio.pedido_id,
            "envio_entregado",
            {"envio_id": envio_id, "numero_envio": envio.numero_envio}
        )
        
        return EnvioResponseDTO.from_orm(envio_actualizado)
    
    def cancelar_envio(self, envio_id: int, motivo: str) -> EnvioResponseDTO:
        """Cancelar un envío"""
        envio = self.envio_repo.get_by_id(envio_id)
        if not envio:
            raise EnvioNotFoundError(envio_id)
        
        if envio.estado in ["entregado", "cancelado"]:
            raise ValueError(f"No se puede cancelar envío en estado '{envio.estado}'")
        
        update_data = EnvioUpdateDTO(
            estado="cancelado",
            observaciones=f"Cancelado: {motivo}"
        )
        
        envio_actualizado = self.envio_repo.update(envio_id, update_data)
        
        self.external_service.encolar_tarea_pedido(
            envio.pedido_id,
            "envio_cancelado",
            {"envio_id": envio_id, "motivo": motivo}
        )
        
        return EnvioResponseDTO.from_orm(envio_actualizado)
