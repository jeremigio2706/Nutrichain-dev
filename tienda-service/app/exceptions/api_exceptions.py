# ============================================================================
# api_exceptions.py
#
# Definición de excepciones personalizadas para el servicio de tienda.
# Incluye excepciones específicas para errores de negocio y validaciones
# relacionadas con pedidos, clientes y operaciones de la tienda.
#
# Este software está licenciado bajo la Licencia MIT.
# Autor: Jorge Ernesto Remigio <jetradercu@yahoo.com>
# ============================================================================

from typing import Optional, Any

class TiendaException(Exception):
    """Excepción base para el servicio de tienda"""
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)

class ClienteNotFoundError(TiendaException):
    """Error cuando no se encuentra un cliente"""
    def __init__(self, cliente_id: int):
        super().__init__(
            f"Cliente con ID {cliente_id} no encontrado",
            "CLIENTE_NOT_FOUND",
            {"cliente_id": cliente_id}
        )

class ClienteInactivoError(TiendaException):
    """Error cuando un cliente está inactivo"""
    def __init__(self, cliente_id: int):
        super().__init__(
            f"Cliente con ID {cliente_id} está inactivo",
            "CLIENTE_INACTIVO",
            {"cliente_id": cliente_id}
        )

class PedidoNotFoundError(TiendaException):
    """Error cuando no se encuentra un pedido"""
    def __init__(self, pedido_id: int):
        super().__init__(
            f"Pedido con ID {pedido_id} no encontrado",
            "PEDIDO_NOT_FOUND",
            {"pedido_id": pedido_id}
        )

class PedidoEstadoInvalidoError(TiendaException):
    """Error cuando el estado del pedido no permite la operación"""
    def __init__(self, pedido_id: int, estado_actual: str, estado_requerido: str):
        super().__init__(
            f"Pedido {pedido_id} está en estado '{estado_actual}', se requiere '{estado_requerido}'",
            "PEDIDO_ESTADO_INVALIDO",
            {"pedido_id": pedido_id, "estado_actual": estado_actual, "estado_requerido": estado_requerido}
        )

class StockInsuficienteError(TiendaException):
    """Error cuando no hay stock suficiente"""
    def __init__(self, producto_id: int, cantidad_solicitada: float, cantidad_disponible: float):
        super().__init__(
            f"Stock insuficiente para producto {producto_id}. Solicitado: {cantidad_solicitada}, Disponible: {cantidad_disponible}",
            "STOCK_INSUFICIENTE",
            {"producto_id": producto_id, "cantidad_solicitada": cantidad_solicitada, "cantidad_disponible": cantidad_disponible}
        )

class LimiteCreditoExcedidoError(TiendaException):
    """Error cuando se excede el límite de crédito del cliente"""
    def __init__(self, cliente_id: int, limite_credito: float, total_pedido: float):
        super().__init__(
            f"Límite de crédito excedido para cliente {cliente_id}. Límite: {limite_credito}, Total pedido: {total_pedido}",
            "LIMITE_CREDITO_EXCEDIDO",
            {"cliente_id": cliente_id, "limite_credito": limite_credito, "total_pedido": total_pedido}
        )

class EnvioNotFoundError(TiendaException):
    """Error cuando no se encuentra un envío"""
    def __init__(self, envio_id: int):
        super().__init__(
            f"Envío con ID {envio_id} no encontrado",
            "ENVIO_NOT_FOUND",
            {"envio_id": envio_id}
        )

class DevolucionNotFoundError(TiendaException):
    """Error cuando no se encuentra una devolución"""
    def __init__(self, devolucion_id: int):
        super().__init__(
            f"Devolución con ID {devolucion_id} no encontrada",
            "DEVOLUCION_NOT_FOUND",
            {"devolucion_id": devolucion_id}
        )

class ServicioExternoError(TiendaException):
    """Error de comunicación con servicios externos"""
    def __init__(self, servicio: str, error_message: str):
        super().__init__(
            f"Error en servicio {servicio}: {error_message}",
            "SERVICIO_EXTERNO_ERROR",
            {"servicio": servicio, "error_message": error_message}
        )

class ValidationError(TiendaException):
    """Error de validación de datos"""
    def __init__(self, field: str, value: Any, message: str):
        super().__init__(
            f"Error de validación en campo '{field}': {message}",
            "VALIDATION_ERROR",
            {"field": field, "value": value, "message": message}
        )

class CodigoClienteExisteError(TiendaException):
    """Error cuando el código de cliente ya existe"""
    def __init__(self, codigo_cliente: str):
        super().__init__(
            f"Ya existe un cliente con código '{codigo_cliente}'",
            "CODIGO_CLIENTE_EXISTE",
            {"codigo_cliente": codigo_cliente}
        )

class NumeroPedidoExisteError(TiendaException):
    """Error cuando el número de pedido ya existe"""
    def __init__(self, numero_pedido: str):
        super().__init__(
            f"Ya existe un pedido con número '{numero_pedido}'",
            "NUMERO_PEDIDO_EXISTE",
            {"numero_pedido": numero_pedido}
        )
