# ============================================================================
# pedido_service.py
#
# Servicio principal para lógica de negocio de pedidos. Orquesta el ciclo
# completo de vida de pedidos incluyendo validaciones, reservas de stock
# y comunicación con servicios externos.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from typing import List, Optional
from sqlalchemy.orm import Session
from decimal import Decimal

from ..repositories.pedido_repository import PedidoRepository, ReservaStockRepository
from ..services.cliente_service import ClienteService
from ..services.external_service import ExternalService
from ..dtos.pedido_dto import (
    PedidoCreateDTO, PedidoUpdateDTO, PedidoConfirmarDTO,
    PedidoResponseDTO, PedidoListResponseDTO
)
from ..exceptions.api_exceptions import (
    PedidoNotFoundError, PedidoEstadoInvalidoError, StockInsuficienteError,
    LimiteCreditoExcedidoError, NumeroPedidoExisteError, ServicioExternoError
)
from ..config import settings

class PedidoService:
    """Servicio para lógica de negocio de pedidos"""
    
    def __init__(self, db: Session):
        self.db = db
        self.pedido_repo = PedidoRepository(db)
        self.reserva_repo = ReservaStockRepository(db)
        self.cliente_service = ClienteService(db)
        self.external_service = ExternalService()
    
    async def crear_pedido(self, pedido_data: PedidoCreateDTO, usuario_creacion: str) -> PedidoResponseDTO:
        """Crear un nuevo pedido con validaciones y reservas de stock"""
        cliente = self.cliente_service.validar_cliente_activo(pedido_data.cliente_id)
        
        total_pedido = sum(
            float(detalle.cantidad * detalle.precio_unitario - detalle.descuento_linea)
            for detalle in pedido_data.detalles
        )
        
        if not self.cliente_service.validar_limite_credito(pedido_data.cliente_id, total_pedido):
            raise LimiteCreditoExcedidoError(
                pedido_data.cliente_id,
                float(cliente.limite_credito),
                total_pedido
            )
        
        productos_consulta = [
            {
                "producto_id": detalle.producto_id,
                "cantidad": float(detalle.cantidad),
                "almacen_id": detalle.almacen_origen_id or pedido_data.almacen_origen_id
            }
            for detalle in pedido_data.detalles
        ]
        
        disponibilidad = await self.external_service.consultar_disponibilidad_stock(productos_consulta)
        
        for item in disponibilidad.get("productos", []):
            if not item.get("disponible", False):
                raise StockInsuficienteError(
                    item.get("producto_id"),
                    item.get("cantidad_solicitada", 0),
                    item.get("cantidad_disponible", 0)
                )
        
        numero_pedido = self.pedido_repo.get_next_numero(settings.numero_pedido_prefix)
        
        pedido = self.pedido_repo.create(pedido_data, numero_pedido, usuario_creacion)
        
        for detalle in pedido_data.detalles:
            self.reserva_repo.create_reserva(
                pedido.id,
                detalle.producto_id,
                detalle.cantidad,
                detalle.almacen_origen_id or pedido_data.almacen_origen_id
            )
        
        self.external_service.encolar_tarea_pedido(
            pedido.id,
            "pedido_creado",
            {"numero_pedido": numero_pedido, "cliente_id": pedido_data.cliente_id}
        )
        
        return PedidoResponseDTO.from_orm(pedido)
    
    def obtener_pedido(self, pedido_id: int) -> PedidoResponseDTO:
        """Obtener un pedido por ID"""
        pedido = self.pedido_repo.get_by_id(pedido_id)
        if not pedido:
            raise PedidoNotFoundError(pedido_id)
        
        return PedidoResponseDTO.from_orm(pedido)
    
    def obtener_pedido_por_numero(self, numero_pedido: str) -> PedidoResponseDTO:
        """Obtener un pedido por número"""
        pedido = self.pedido_repo.get_by_numero(numero_pedido)
        if not pedido:
            raise PedidoNotFoundError(f"Número: {numero_pedido}")
        
        return PedidoResponseDTO.from_orm(pedido)
    
    def listar_pedidos(self, page: int = 1, page_size: int = 100, 
                      cliente_id: Optional[int] = None, estado: Optional[str] = None) -> PedidoListResponseDTO:
        """Listar pedidos con filtros y paginación"""
        skip = (page - 1) * page_size
        pedidos = self.pedido_repo.get_all(skip=skip, limit=page_size, cliente_id=cliente_id, estado=estado)
        total = self.pedido_repo.count(cliente_id=cliente_id, estado=estado)
        
        pedidos_dto = [PedidoResponseDTO.from_orm(pedido) for pedido in pedidos]
        
        return PedidoListResponseDTO(
            pedidos=pedidos_dto,
            total=total,
            page=page,
            page_size=page_size
        )
    
    def actualizar_pedido(self, pedido_id: int, pedido_data: PedidoUpdateDTO) -> PedidoResponseDTO:
        """Actualizar un pedido (solo en estados permitidos)"""
        pedido = self.pedido_repo.get_by_id(pedido_id)
        if not pedido:
            raise PedidoNotFoundError(pedido_id)
        
        if pedido.estado not in ["borrador", "pendiente"]:
            raise PedidoEstadoInvalidoError(pedido_id, pedido.estado, "borrador o pendiente")
        
        pedido_actualizado = self.pedido_repo.update(pedido_id, pedido_data)
        return PedidoResponseDTO.from_orm(pedido_actualizado)
    
    async def confirmar_pedido(self, pedido_id: int, confirmacion_data: PedidoConfirmarDTO) -> PedidoResponseDTO:
        """Confirmar un pedido y ejecutar movimientos de stock"""
        pedido = self.pedido_repo.get_by_id(pedido_id)
        if not pedido:
            raise PedidoNotFoundError(pedido_id)
        
        if pedido.estado != "borrador":
            raise PedidoEstadoInvalidoError(pedido_id, pedido.estado, "borrador")
        
        if self.external_service.esta_pedido_procesando(pedido_id):
            raise PedidoEstadoInvalidoError(pedido_id, "procesando", "disponible")
        
        self.external_service.marcar_pedido_procesando(pedido_id)
        
        try:
            productos_movimiento = [
                {
                    "producto_id": detalle.producto_id,
                    "cantidad": float(detalle.cantidad),
                    "almacen_origen_id": pedido.almacen_origen_id
                }
                for detalle in pedido.detalles
            ]
            
            movimiento_result = await self.external_service.crear_movimiento_salida(
                productos_movimiento,
                f"PEDIDO_{pedido.numero_pedido}"
            )
            
            if movimiento_result.get("success"):
                pedido_confirmado = self.pedido_repo.update_estado(
                    pedido_id, 
                    "confirmado", 
                    confirmacion_data.usuario_aprobacion
                )
                
                self.reserva_repo.delete_reservas(pedido_id)
                
                self.external_service.encolar_tarea_pedido(
                    pedido_id,
                    "pedido_confirmado",
                    {"movimiento_id": movimiento_result.get("movimiento_id")}
                )
                
                return PedidoResponseDTO.from_orm(pedido_confirmado)
            else:
                raise ServicioExternoError("almacen", "Error al procesar movimiento de stock")
        
        except Exception as e:
            self.pedido_repo.update_estado(pedido_id, "fallido")
            raise e
        finally:
            self.external_service.liberar_pedido_procesando(pedido_id)
    
    def cancelar_pedido(self, pedido_id: int, motivo: str, usuario: str) -> PedidoResponseDTO:
        """Cancelar un pedido"""
        pedido = self.pedido_repo.get_by_id(pedido_id)
        if not pedido:
            raise PedidoNotFoundError(pedido_id)
        
        if pedido.estado not in ["borrador", "pendiente", "confirmado"]:
            raise PedidoEstadoInvalidoError(pedido_id, pedido.estado, "borrador, pendiente o confirmado")
        
        update_data = PedidoUpdateDTO(
            estado="cancelado",
            motivo_cancelacion=motivo,
            usuario_aprobacion=usuario
        )
        
        pedido_cancelado = self.pedido_repo.update(pedido_id, update_data)
        
        self.reserva_repo.liberar_reservas(pedido_id)
        
        self.external_service.encolar_tarea_pedido(
            pedido_id,
            "pedido_cancelado",
            {"motivo": motivo, "usuario": usuario}
        )
        
        return PedidoResponseDTO.from_orm(pedido_cancelado)
