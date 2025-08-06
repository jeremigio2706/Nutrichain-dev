# ============================================================================
# devolucion_service.py
#
# Servicio de lógica de negocio para devoluciones. Gestiona el proceso
# completo de devoluciones incluyendo inspección, aprobación y 
# reintegración de inventario.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from typing import List, Optional
from sqlalchemy.orm import Session

from ..repositories.devolucion_repository import DevolucionRepository
from ..repositories.pedido_repository import PedidoRepository
from ..repositories.envio_repository import EnvioRepository
from ..services.external_service import ExternalService
from ..dtos.devolucion_dto import (
    DevolucionCreateDTO, DevolucionUpdateDTO, 
    DevolucionResponseDTO, DevolucionListResponseDTO
)
from ..exceptions.api_exceptions import (
    DevolucionNotFoundError, PedidoNotFoundError, 
    EnvioNotFoundError, PedidoEstadoInvalidoError
)
from ..config import settings

class DevolucionService:
    """Servicio para lógica de negocio de devoluciones"""
    
    def __init__(self, db: Session):
        self.db = db
        self.devolucion_repo = DevolucionRepository(db)
        self.pedido_repo = PedidoRepository(db)
        self.envio_repo = EnvioRepository(db)
        self.external_service = ExternalService()
    
    def crear_devolucion(self, devolucion_data: DevolucionCreateDTO) -> DevolucionResponseDTO:
        """Crear una nueva devolución"""
        pedido = self.pedido_repo.get_by_id(devolucion_data.pedido_id)
        if not pedido:
            raise PedidoNotFoundError(devolucion_data.pedido_id)
        
        if pedido.estado not in ["entregado", "enviado"]:
            raise PedidoEstadoInvalidoError(
                devolucion_data.pedido_id,
                pedido.estado,
                "entregado o enviado"
            )
        
        if devolucion_data.envio_id:
            envio = self.envio_repo.get_by_id(devolucion_data.envio_id)
            if not envio:
                raise EnvioNotFoundError(devolucion_data.envio_id)
            
            if envio.pedido_id != devolucion_data.pedido_id:
                raise ValueError("El envío no corresponde al pedido especificado")
        
        numero_devolucion = self.devolucion_repo.get_next_numero(settings.numero_devolucion_prefix)
        
        devolucion = self.devolucion_repo.create(devolucion_data, numero_devolucion)
        
        self.external_service.encolar_tarea_pedido(
            devolucion_data.pedido_id,
            "devolucion_creada",
            {
                "devolucion_id": devolucion.id,
                "numero_devolucion": numero_devolucion,
                "motivo": devolucion_data.motivo
            }
        )
        
        return DevolucionResponseDTO.from_orm(devolucion)
    
    def obtener_devolucion(self, devolucion_id: int) -> DevolucionResponseDTO:
        """Obtener una devolución por ID"""
        devolucion = self.devolucion_repo.get_by_id(devolucion_id)
        if not devolucion:
            raise DevolucionNotFoundError(devolucion_id)
        
        return DevolucionResponseDTO.from_orm(devolucion)
    
    def obtener_devolucion_por_numero(self, numero_devolucion: str) -> DevolucionResponseDTO:
        """Obtener una devolución por número"""
        devolucion = self.devolucion_repo.get_by_numero(numero_devolucion)
        if not devolucion:
            raise DevolucionNotFoundError(f"Número: {numero_devolucion}")
        
        return DevolucionResponseDTO.from_orm(devolucion)
    
    def obtener_devoluciones_pedido(self, pedido_id: int) -> List[DevolucionResponseDTO]:
        """Obtener todas las devoluciones de un pedido"""
        if not self.pedido_repo.get_by_id(pedido_id):
            raise PedidoNotFoundError(pedido_id)
        
        devoluciones = self.devolucion_repo.get_by_pedido(pedido_id)
        return [DevolucionResponseDTO.from_orm(devolucion) for devolucion in devoluciones]
    
    def listar_devoluciones(self, page: int = 1, page_size: int = 100, 
                           estado: Optional[str] = None) -> DevolucionListResponseDTO:
        """Listar devoluciones con filtros y paginación"""
        skip = (page - 1) * page_size
        devoluciones = self.devolucion_repo.get_all(skip=skip, limit=page_size, estado=estado)
        total = self.devolucion_repo.count(estado=estado)
        
        devoluciones_dto = [DevolucionResponseDTO.from_orm(devolucion) for devolucion in devoluciones]
        
        return DevolucionListResponseDTO(
            devoluciones=devoluciones_dto,
            total=total,
            page=page,
            page_size=page_size
        )
    
    def actualizar_devolucion(self, devolucion_id: int, devolucion_data: DevolucionUpdateDTO) -> DevolucionResponseDTO:
        """Actualizar una devolución"""
        devolucion = self.devolucion_repo.get_by_id(devolucion_id)
        if not devolucion:
            raise DevolucionNotFoundError(devolucion_id)
        
        devolucion_actualizada = self.devolucion_repo.update(devolucion_id, devolucion_data)
        
        if devolucion_data.estado and devolucion_data.estado != devolucion.estado:
            self.external_service.encolar_tarea_pedido(
                devolucion.pedido_id,
                "devolucion_actualizada",
                {
                    "devolucion_id": devolucion_id,
                    "estado_anterior": devolucion.estado,
                    "estado_nuevo": devolucion_data.estado
                }
            )
        
        return DevolucionResponseDTO.from_orm(devolucion_actualizada)
    
    def inspeccionar_devolucion(self, devolucion_id: int, usuario: str) -> DevolucionResponseDTO:
        """Marcar devolución como inspeccionada"""
        devolucion = self.devolucion_repo.get_by_id(devolucion_id)
        if not devolucion:
            raise DevolucionNotFoundError(devolucion_id)
        
        if devolucion.estado != "recibida":
            raise ValueError(f"Devolución debe estar 'recibida', actual: {devolucion.estado}")
        
        devolucion_actualizada = self.devolucion_repo.update_estado(
            devolucion_id, 
            "inspeccionada", 
            usuario
        )
        
        self.external_service.encolar_tarea_pedido(
            devolucion.pedido_id,
            "devolucion_inspeccionada",
            {"devolucion_id": devolucion_id, "inspector": usuario}
        )
        
        return DevolucionResponseDTO.from_orm(devolucion_actualizada)
    
    async def aprobar_devolucion(self, devolucion_id: int, usuario: str) -> DevolucionResponseDTO:
        """Aprobar devolución y procesar reintegro de inventario"""
        devolucion = self.devolucion_repo.get_by_id(devolucion_id)
        if not devolucion:
            raise DevolucionNotFoundError(devolucion_id)
        
        if devolucion.estado != "inspeccionada":
            raise ValueError(f"Devolución debe estar 'inspeccionada', actual: {devolucion.estado}")
        
        productos_reintegro = []
        for detalle in devolucion.detalles:
            if detalle.accion == "reintegrar_inventario":
                productos_reintegro.append({
                    "producto_id": detalle.producto_id,
                    "cantidad": float(detalle.cantidad_devuelta),
                    "almacen_destino_id": 1
                })
        
        if productos_reintegro:
            await self.external_service.crear_movimiento_entrada(
                productos_reintegro,
                f"DEVOLUCION_{devolucion.numero_devolucion}"
            )
        
        devolucion_aprobada = self.devolucion_repo.update_estado(
            devolucion_id, 
            "aprobada", 
            usuario
        )
        
        self.external_service.encolar_tarea_pedido(
            devolucion.pedido_id,
            "devolucion_aprobada",
            {
                "devolucion_id": devolucion_id,
                "productos_reintegrados": len(productos_reintegro),
                "aprobador": usuario
            }
        )
        
        return DevolucionResponseDTO.from_orm(devolucion_aprobada)
    
    def rechazar_devolucion(self, devolucion_id: int, usuario: str, motivo: str) -> DevolucionResponseDTO:
        """Rechazar una devolución"""
        devolucion = self.devolucion_repo.get_by_id(devolucion_id)
        if not devolucion:
            raise DevolucionNotFoundError(devolucion_id)
        
        if devolucion.estado not in ["recibida", "inspeccionada"]:
            raise ValueError(f"Devolución debe estar 'recibida' o 'inspeccionada', actual: {devolucion.estado}")
        
        update_data = DevolucionUpdateDTO(
            estado="rechazada",
            usuario_procesamiento=usuario,
            descripcion=f"Rechazada: {motivo}"
        )
        
        devolucion_rechazada = self.devolucion_repo.update(devolucion_id, update_data)
        
        self.external_service.encolar_tarea_pedido(
            devolucion.pedido_id,
            "devolucion_rechazada",
            {"devolucion_id": devolucion_id, "motivo": motivo, "usuario": usuario}
        )
        
        return DevolucionResponseDTO.from_orm(devolucion_rechazada)
    
    async def procesar_devolucion(self, devolucion_id: int, usuario: str) -> DevolucionResponseDTO:
        """Procesar completamente una devolución aprobada"""
        devolucion = self.devolucion_repo.get_by_id(devolucion_id)
        if not devolucion:
            raise DevolucionNotFoundError(devolucion_id)
        
        if devolucion.estado != "aprobada":
            raise ValueError(f"Devolución debe estar 'aprobada', actual: {devolucion.estado}")
        
        devolucion_procesada = self.devolucion_repo.update_estado(
            devolucion_id, 
            "procesada", 
            usuario
        )
        
        self.external_service.encolar_tarea_pedido(
            devolucion.pedido_id,
            "devolucion_procesada",
            {"devolucion_id": devolucion_id, "procesador": usuario}
        )
        
        return DevolucionResponseDTO.from_orm(devolucion_procesada)
