"""
Servicio para gestión de movimientos de inventario
RESPONSABILIDAD ÚNICA: Gestionar todos los movimientos que afectan el stock

INTEGRACIÓN NIVEL SENIOR:
- Validación de productos con servicio de Catálogo (fail-fast)
- Transacciones atómicas para integridad de datos
- Auditabilidad completa de todos los cambios de inventario
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..repositories.movimiento_repository import MovimientoRepository
from ..repositories.stock_repository import StockRepository
from ..services.catalogo_integration_service import catalogo_service
from ..dtos.movimiento_dto import (
    MovimientoEntradaDTO as MovimientoEntrada,
    MovimientoSalidaDTO as MovimientoSalida, 
    MovimientoTransferenciaDTO as MovimientoTransferencia,
    MovimientoAjusteInicialDTO as MovimientoAjusteInicial,
    MovimientoResponseDTO as MovimientoResponse,
    MovimientoListDTO as MovimientoList,
    TipoMovimientoEnum, 
    EstadoMovimientoEnum
)
from ..exceptions import (
    NotFoundError,
    ValidationError,
    BusinessLogicError
)


class MovimientoService:
    """
    Servicio para gestión de movimientos de inventario
    
    PRINCIPIO DE RESPONSABILIDAD ÚNICA:
    - Este servicio es la ÚNICA fuente de verdad para modificar stock
    - Toda entrada, salida o transferencia DEBE pasar por aquí
    - Garantiza consistencia y auditoría completa de movimientos
    - Maneja transacciones atómicas (movimiento + actualización stock)
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.movimiento_repository = MovimientoRepository(db)
        self.stock_repository = StockRepository(db)
    
    def _validar_producto(self, producto_id: int) -> None:
        """Validar que el producto existe y está activo en el catálogo"""
        if not catalogo_service.verificar_producto_existe_sync(producto_id):
            raise NotFoundError(f"El producto con ID {producto_id} no existe en el catálogo")
    
    def _validar_almacen(self, almacen_id: int) -> None:
        """Validar que el almacén existe y está activo"""
        from ..models.almacen import Almacen
        almacen = self.db.query(Almacen).filter(Almacen.id == almacen_id).first()
        
        if not almacen:
            raise NotFoundError(f"El almacén con ID {almacen_id} no existe")
        
        if not almacen.activo:
            raise ValidationError(f"El almacén '{almacen.nombre}' no está activo")
    
    def _validar_stock_disponible(self, producto_id: int, almacen_id: int, cantidad_requerida: float) -> None:
        """Validar que hay stock suficiente para una salida"""
        stock = self.stock_repository.get_by_almacen_and_producto(almacen_id, producto_id)
        
        if not stock:
            raise ValidationError(
                f"No hay stock del producto {producto_id} en el almacén {almacen_id}"
            )
        
        cantidad_disponible = stock.cantidad_actual - stock.cantidad_reservada
        if cantidad_disponible < cantidad_requerida:
            raise BusinessLogicError(
                f"Stock insuficiente para producto {producto_id} en almacén {almacen_id}. "
                f"Disponible: {cantidad_disponible}, Requerido: {cantidad_requerida}"
            )
    
    def crear_movimiento_entrada(self, movimiento_data: MovimientoEntrada) -> MovimientoResponse:
        """
        Crear movimiento de entrada con validaciones completas
        
        Validaciones automáticas:
        - Existencia del producto en catálogo
        - Estado activo del producto
        - Existencia y estado activo del almacén
        - Creación automática de stock si no existe
        """
        try:
            # Validaciones centralizadas
            self._validar_producto(movimiento_data.producto_id)
            self._validar_almacen(movimiento_data.almacen_destino_id)
            
            # Buscar o crear stock
            stock = self.stock_repository.get_by_almacen_and_producto(
                movimiento_data.almacen_destino_id, 
                movimiento_data.producto_id
            )
            
            if not stock:
                # Si no existe stock, crear uno nuevo
                from ..dtos.stock_dto import StockCreateDTO
                stock_data = StockCreateDTO(
                    producto_id=movimiento_data.producto_id,
                    almacen_id=movimiento_data.almacen_destino_id,
                    cantidad_actual=0,
                    cantidad_reservada=0
                )
                stock = self.stock_repository.create(stock_data.model_dump())
            
            # Crear el movimiento
            movimiento_dict = movimiento_data.model_dump()
            movimiento_dict['tipo_movimiento'] = TipoMovimientoEnum.ENTRADA
            movimiento_dict['estado'] = EstadoMovimientoEnum.PROCESADO
            movimiento_dict['fecha_movimiento'] = datetime.utcnow()
            movimiento_dict['producto_id'] = movimiento_data.producto_id
            
            movimiento = self.movimiento_repository.create(movimiento_dict)
            
            # Actualizar stock
            stock.cantidad_actual += movimiento_data.cantidad
            stock.updated_at = datetime.utcnow()
            
            self.db.commit()
            return MovimientoResponse.model_validate(movimiento)
            
        except Exception as e:
            self.db.rollback()
            if isinstance(e, (NotFoundError, ValidationError, BusinessLogicError)):
                raise
            raise BusinessLogicError(f"Error al crear movimiento de entrada: {str(e)}")
            self.db.rollback()
            if isinstance(e, (NotFoundError, ValidationError, BusinessLogicError)):
                raise
            raise BusinessLogicError(f"Error al crear movimiento de entrada: {str(e)}")
    
    def crear_movimiento_salida(self, movimiento_data: MovimientoSalida) -> MovimientoResponse:
        """
        Crear movimiento de salida con validaciones completas
        
        Validaciones automáticas:
        - Existencia del producto en catálogo
        - Estado activo del producto
        - Existencia y estado activo del almacén
        - Disponibilidad de stock suficiente
        """
        try:
            # Validaciones centralizadas
            self._validar_producto(movimiento_data.producto_id)
            self._validar_almacen(movimiento_data.almacen_origen_id)
            self._validar_stock_disponible(
                movimiento_data.producto_id, 
                movimiento_data.almacen_origen_id, 
                movimiento_data.cantidad
            )
            
            # Buscar stock
            stock = self.stock_repository.get_by_almacen_and_producto(
                movimiento_data.almacen_origen_id, 
                movimiento_data.producto_id
            )
            
            # Crear el movimiento
            movimiento_dict = movimiento_data.model_dump()
            movimiento_dict['tipo_movimiento'] = TipoMovimientoEnum.SALIDA
            movimiento_dict['estado'] = EstadoMovimientoEnum.PROCESADO
            movimiento_dict['fecha_movimiento'] = datetime.utcnow()
            movimiento_dict['producto_id'] = movimiento_data.producto_id
            
            movimiento = self.movimiento_repository.create(movimiento_dict)
            
            # Actualizar stock
            stock.cantidad_actual -= movimiento_data.cantidad
            stock.updated_at = datetime.utcnow()
            
            self.db.commit()
            return MovimientoResponse.model_validate(movimiento)
            
        except Exception as e:
            self.db.rollback()
            if isinstance(e, (NotFoundError, ValidationError, BusinessLogicError)):
                raise
            raise BusinessLogicError(f"Error al crear movimiento de salida: {str(e)}")
            
            return MovimientoResponse.model_validate(movimiento)
            
        except Exception as e:
            self.db.rollback()
            if isinstance(e, (NotFoundError, ValidationError, BusinessLogicError)):
                raise
            raise BusinessLogicError(f"Error al crear movimiento de salida: {str(e)}")
    
    def crear_movimiento_transferencia(self, movimiento_data: MovimientoTransferencia) -> MovimientoResponse:
        """
        Crear movimiento de transferencia entre almacenes (TRANSACCIÓN ATÓMICA)
        
        NIVEL SENIOR - VALIDACIONES CRÍTICAS:
        1. Verificar existencia del producto en Catálogo (fail-fast)
        2. Validar stock disponible en origen
        3. Crear o actualizar stock en destino
        4. Operación atómica para garantizar consistencia
        """
        try:
            # PASO 1: VALIDACIÓN CRÍTICA - Producto debe existir en Catálogo
            if not catalogo_service.verificar_producto_existe_sync(movimiento_data.producto_id):
                raise NotFoundError(f"El producto con ID {movimiento_data.producto_id} no existe en el catálogo")
            
            # PASO 2: Buscar stock origen por almacén y producto
            stock_origen = self.stock_repository.get_by_almacen_and_producto(
                movimiento_data.almacen_origen_id, 
                movimiento_data.producto_id
            )
            if not stock_origen:
                raise NotFoundError(f"No hay stock del producto {movimiento_data.producto_id} en almacén {movimiento_data.almacen_origen_id}")
            
            # Validación de stock disponible en origen
            cantidad_disponible = stock_origen.cantidad_actual - stock_origen.cantidad_reservada
            if cantidad_disponible < movimiento_data.cantidad:
                raise ValidationError(
                    f"Stock insuficiente en origen. Disponible: {cantidad_disponible}, "
                    f"Solicitado: {movimiento_data.cantidad}"
                )
            
            # Buscar stock en almacén destino para el mismo producto
            stock_destino = self.stock_repository.get_by_producto_y_almacen(
                movimiento_data.producto_id,
                movimiento_data.almacen_destino_id
            )
            
            # Crear el movimiento ANTES de actualizar stocks (para auditoría)
            movimiento_dict = movimiento_data.model_dump()
            movimiento_dict['tipo_movimiento'] = TipoMovimientoEnum.TRANSFERENCIA
            movimiento_dict['estado'] = EstadoMovimientoEnum.PROCESADO
            movimiento_dict['fecha_movimiento'] = datetime.utcnow()
            
            movimiento = self.movimiento_repository.create(movimiento_dict)
            
            # Actualizar stock origen (REDUCIR)
            stock_origen.cantidad_actual -= movimiento_data.cantidad
            stock_origen.updated_at = datetime.utcnow()
            
            # Crear o actualizar stock destino (AUMENTAR)
            if stock_destino:
                stock_destino.cantidad_actual += movimiento_data.cantidad
                stock_destino.updated_at = datetime.utcnow()
            else:
                # Crear nuevo stock en destino con propiedades heredadas
                nuevo_stock_data = {
                    'producto_id': movimiento_data.producto_id,
                    'almacen_id': movimiento_data.almacen_destino_id,
                    'cantidad_actual': movimiento_data.cantidad,
                    'cantidad_reservada': 0,
                    'cantidad_minima': stock_origen.cantidad_minima,
                    'cantidad_maxima': stock_origen.cantidad_maxima,
                    'costo_unitario': stock_origen.costo_unitario,
                    'updated_at': datetime.utcnow()
                }
                self.stock_repository.create(nuevo_stock_data)
            
            self.db.commit()
            
            return MovimientoResponse.model_validate(movimiento)
            
        except Exception as e:
            self.db.rollback()
            if isinstance(e, (NotFoundError, ValidationError, BusinessLogicError)):
                raise
            raise BusinessLogicError(f"Error al crear movimiento de transferencia: {str(e)}")
    
    def crear_stock_inicial_auditado(self, ajuste_data) -> MovimientoResponse:
        """
        MÉTODO NIVEL SENIOR: Crear stock inicial de forma completamente auditada
        
        Este es el reemplazo para el POST /stock/ eliminado.
        TODO stock inicial debe tener un movimiento de ajuste que lo justifique.
        
        VALIDACIONES CRÍTICAS:
        1. Verificar existencia del producto en Catálogo (fail-fast)
        2. Verificar que no exista stock previo (prevenir duplicados)
        3. Crear stock con movimiento de ajuste inicial auditado
        """
        try:
            # PASO 1: VALIDACIÓN CRÍTICA - Producto debe existir en Catálogo
            if not catalogo_service.verificar_producto_existe_sync(ajuste_data.producto_id):
                raise NotFoundError(f"El producto con ID {ajuste_data.producto_id} no existe en el catálogo")
            
            # PASO 2: Verificar que no exista stock previo
            stock_existente = self.stock_repository.get_by_almacen_and_producto(
                ajuste_data.almacen_id, 
                ajuste_data.producto_id
            )
            if stock_existente:
                raise ValidationError(
                    f"Ya existe stock para el producto {ajuste_data.producto_id} "
                    f"en el almacén {ajuste_data.almacen_id}. "
                    f"Use un movimiento de entrada para aumentar cantidad."
                )
            
            # PASO 3: Crear stock inicial con movimiento de ajuste
            stock_data = {
                'producto_id': ajuste_data.producto_id,
                'almacen_id': ajuste_data.almacen_id,
                'cantidad_actual': ajuste_data.cantidad_inicial,
                'cantidad_reservada': 0,
                'cantidad_minima': ajuste_data.cantidad_minima or 0,
                'cantidad_maxima': ajuste_data.cantidad_maxima or 999999,
                'costo_unitario': ajuste_data.costo_unitario or 0,
                'updated_at': datetime.utcnow()
            }
            
            stock = self.stock_repository.create(stock_data)
            
            # PASO 4: Crear movimiento de ajuste inicial para auditabilidad
            movimiento_dict = {
                'producto_id': ajuste_data.producto_id,
                'almacen_destino_id': ajuste_data.almacen_id,
                'tipo_movimiento': TipoMovimientoEnum.AJUSTE,
                'cantidad': ajuste_data.cantidad_inicial,
                'motivo': ajuste_data.motivo or "Creación de stock inicial",
                'usuario': ajuste_data.usuario,
                'observaciones': ajuste_data.observaciones,
                'estado': EstadoMovimientoEnum.PROCESADO,
                'fecha_movimiento': datetime.utcnow(),
                'costo_unitario': ajuste_data.costo_unitario
            }
            
            movimiento = self.movimiento_repository.create(movimiento_dict)
            
            self.db.commit()
            
            return MovimientoResponse.model_validate(movimiento)
            
        except Exception as e:
            self.db.rollback()
            if isinstance(e, (NotFoundError, ValidationError, BusinessLogicError)):
                raise
            raise BusinessLogicError(f"Error al crear stock inicial auditado: {str(e)}")
    
    def listar_movimientos(
        self,
        skip: int = 0,
        limit: int = 100,
        filtros: Optional[Dict[str, Any]] = None
    ) -> MovimientoList:
        """Listar movimientos con filtros"""
        try:
            movimientos = self.movimiento_repository.get_multi(
                skip=skip,
                limit=limit,
                filters=filtros
            )
            
            total = self.movimiento_repository.count(filtros)
            
            movimientos_response = [
                MovimientoResponse.model_validate(mov) for mov in movimientos
            ]
            
            return MovimientoList(
                movimientos=movimientos_response,
                total=total,
                skip=skip,
                limit=limit
            )
            
        except Exception as e:
            raise BusinessLogicError(f"Error al listar movimientos: {str(e)}")
    
    def obtener_movimiento(self, movimiento_id: int) -> MovimientoResponse:
        """Obtener movimiento por ID"""
        movimiento = self.movimiento_repository.get(movimiento_id)
        if not movimiento:
            raise NotFoundError(f"Movimiento con ID {movimiento_id} no encontrado")
        
        return MovimientoResponse.model_validate(movimiento)
    
    def obtener_movimientos_por_almacen(
        self,
        almacen_id: int,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        tipo_movimiento: Optional[TipoMovimientoEnum] = None,
        skip: int = 0,
        limit: int = 100
    ) -> MovimientoList:
        """Obtener movimientos por almacén con filtros"""
        try:
            movimientos = self.movimiento_repository.get_by_almacen(
                almacen_id=almacen_id,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                tipo_movimiento=tipo_movimiento,
                skip=skip,
                limit=limit
            )
            
            total = self.movimiento_repository.count_by_almacen(
                almacen_id=almacen_id,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                tipo_movimiento=tipo_movimiento
            )
            
            movimientos_response = [
                MovimientoResponse.model_validate(mov) for mov in movimientos
            ]
            
            return MovimientoList(
                movimientos=movimientos_response,
                total=total,
                skip=skip,
                limit=limit
            )
            
        except Exception as e:
            raise BusinessLogicError(f"Error al obtener movimientos por almacén: {str(e)}")
    
    def obtener_reporte_movimientos(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        almacen_id: Optional[int] = None,
        tipo_movimiento: Optional[TipoMovimientoEnum] = None
    ) -> Dict[str, Any]:
        """Obtener reporte de movimientos"""
        try:
            return self.movimiento_repository.get_reporte_movimientos(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                almacen_id=almacen_id,
                tipo_movimiento=tipo_movimiento
            )
        except Exception as e:
            raise BusinessLogicError(f"Error al generar reporte de movimientos: {str(e)}")
    
    def obtener_stock_post_movimiento(self, producto_id: int, almacen_id: int) -> Optional[dict]:
        """
        Obtener información del stock después de realizar un movimiento
        Útil para verificar el estado del stock tras operaciones
        """
        try:
            stock = self.stock_repository.get_by_almacen_and_producto(almacen_id, producto_id)
            if not stock:
                return None
            
            return {
                "stock_id": stock.id,
                "producto_id": stock.producto_id,
                "almacen_id": stock.almacen_id,
                "cantidad_actual": stock.cantidad_actual,
                "cantidad_disponible": stock.cantidad_disponible,
                "fecha_actualizacion": stock.updated_at
            }
        except Exception as e:
            raise BusinessLogicError(f"Error al obtener stock post-movimiento: {str(e)}")
    
    def crear_movimiento_entrada_con_stock(self, movimiento_data: MovimientoEntrada) -> dict:
        """
        Crear movimiento de entrada y devolver información del movimiento y stock
        """
        try:
            # Crear el movimiento
            movimiento = self.crear_movimiento_entrada(movimiento_data)
            
            # Obtener información del stock actualizado
            stock_info = self.obtener_stock_post_movimiento(
                movimiento_data.producto_id, 
                movimiento_data.almacen_destino_id
            )
            
            return {
                "movimiento": movimiento,
                "stock_actualizado": stock_info
            }
        except Exception as e:
            self.db.rollback()
            if isinstance(e, (NotFoundError, ValidationError, BusinessLogicError)):
                raise
            raise BusinessLogicError(f"Error al crear movimiento de entrada con stock: {str(e)}")
    
    def crear_movimiento_salida_con_stock(self, movimiento_data: MovimientoSalida) -> dict:
        """
        Crear movimiento de salida y devolver información del movimiento y stock
        """
        try:
            # Crear el movimiento
            movimiento = self.crear_movimiento_salida(movimiento_data)
            
            # Obtener información del stock actualizado
            stock_info = self.obtener_stock_post_movimiento(
                movimiento_data.producto_id, 
                movimiento_data.almacen_origen_id
            )
            
            return {
                "movimiento": movimiento,
                "stock_actualizado": stock_info
            }
        except Exception as e:
            self.db.rollback()
            if isinstance(e, (NotFoundError, ValidationError, BusinessLogicError)):
                raise
            raise BusinessLogicError(f"Error al crear movimiento de salida con stock: {str(e)}")

    # =====================================================================
    # MÉTODOS PARA MOVIMIENTOS MÚLTIPLES (BATCH OPERATIONS)
    # =====================================================================

    def crear_movimientos_salida_multiple(self, movimientos_data: List[MovimientoSalida]) -> List[MovimientoResponse]:
        """
        Crear múltiples movimientos de salida con validaciones completas
        
        Procesamiento atómico: si un movimiento falla, toda la operación se revierte
        Cada movimiento puede ser de diferentes productos y almacenes
        """
        if not movimientos_data:
            raise ValidationError("Debe proporcionar al menos un movimiento")
        
        try:
            # Validar todos los movimientos antes de procesar
            for movimiento_data in movimientos_data:
                self._validar_producto(movimiento_data.producto_id)
                self._validar_almacen(movimiento_data.almacen_origen_id)
                self._validar_stock_disponible(
                    movimiento_data.producto_id,
                    movimiento_data.almacen_origen_id,
                    movimiento_data.cantidad
                )
            
            # Procesar todos los movimientos
            movimientos_creados = []
            for movimiento_data in movimientos_data:
                movimiento_creado = self.crear_movimiento_salida(movimiento_data)
                movimientos_creados.append(movimiento_creado)
            
            return movimientos_creados
            
        except Exception as e:
            self.db.rollback()
            if isinstance(e, (NotFoundError, ValidationError, BusinessLogicError)):
                raise
            raise BusinessLogicError(f"Error al crear movimientos de salida múltiples: {str(e)}")

    def crear_movimientos_entrada_multiple(self, movimientos_data: List[MovimientoEntrada]) -> List[MovimientoResponse]:
        """
        Crear múltiples movimientos de entrada con validaciones completas
        
        Procesamiento atómico: si un movimiento falla, toda la operación se revierte
        Cada movimiento puede ser de diferentes productos y almacenes
        """
        if not movimientos_data:
            raise ValidationError("Debe proporcionar al menos un movimiento")
        
        try:
            # Validar todos los movimientos antes de procesar
            for movimiento_data in movimientos_data:
                self._validar_producto(movimiento_data.producto_id)
                self._validar_almacen(movimiento_data.almacen_destino_id)
            
            # Procesar todos los movimientos
            movimientos_creados = []
            for movimiento_data in movimientos_data:
                movimiento_creado = self.crear_movimiento_entrada(movimiento_data)
                movimientos_creados.append(movimiento_creado)
            
            return movimientos_creados
            
        except Exception as e:
            self.db.rollback()
            if isinstance(e, (NotFoundError, ValidationError, BusinessLogicError)):
                raise
            raise BusinessLogicError(f"Error al crear movimientos de entrada múltiples: {str(e)}")
