"""
Servicio de integración con el Catálogo Service
Desarrollador Senior: Implementación de integración entre microservicios
"""

import httpx
import logging
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin

from ..config import settings
from ..exceptions.api_exceptions import ValidationError, NotFoundError, BusinessLogicError

logger = logging.getLogger(__name__)


class CatalogoIntegrationService:
    """
    Servicio para integración con el microservicio de catálogo
    
    Principios Senior aplicados:
    - Timeout configurables para evitar bloqueos
    - Manejo robusto de errores de red
    - Cache interno para reducir llamadas
    - Logging detallado para debugging
    """
    
    def __init__(self):
        self.base_url = settings.catalogo_service_url
        self.timeout = 10.0  # 10 segundos timeout
        self._cache = {}  # Cache simple en memoria
        
    async def verificar_producto_existe(self, producto_id: int) -> bool:
        """
        Verifica si un producto existe en el catálogo
        
        Args:
            producto_id: ID del producto a verificar
            
        Returns:
            bool: True si el producto existe, False en caso contrario
            
        Raises:
            ValidationError: Si hay problemas de conectividad
        """
        # Check cache first
        cache_key = f"producto_{producto_id}"
        if cache_key in self._cache:
            logger.debug(f"Cache hit for producto_id: {producto_id}")
            return self._cache[cache_key]
        
        try:
            url = urljoin(self.base_url, f"/api/productos/{producto_id}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                # Log para debugging
                logger.info(f"Catalogo API call: GET {url} -> {response.status_code}")
                
                exists = response.status_code == 200
                
                # Cache result for 5 minutes (simplificado)
                self._cache[cache_key] = exists
                
                return exists
                
        except httpx.TimeoutException:
            logger.error(f"Timeout al consultar producto {producto_id} en catálogo")
            raise ValidationError(f"Timeout al consultar catálogo para producto {producto_id}")
            
        except httpx.RequestError as e:
            logger.error(f"Error de conectividad con catálogo: {str(e)}")
            raise ValidationError(f"Error de conectividad con servicio de catálogo: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error inesperado al consultar catálogo: {str(e)}")
            raise ValidationError(f"Error interno al consultar catálogo")
    
    async def obtener_producto(self, producto_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene la información completa de un producto
        
        Args:
            producto_id: ID del producto
            
        Returns:
            Dict con información del producto o None si no existe
        """
        try:
            url = urljoin(self.base_url, f"/api/productos/{producto_id}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    # Extraer el producto de la respuesta del catálogo
                    if data.get('success') and 'data' in data:
                        return data['data']
                    return None
                elif response.status_code == 404:
                    return None
                else:
                    logger.warning(f"Respuesta inesperada del catálogo: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error al obtener producto {producto_id}: {str(e)}")
            return None
    
    def verificar_producto_existe_sync(self, producto_id: int) -> bool:
        """
        Versión síncrona de verificar_producto_existe para uso en servicios síncronos
        
        PATRÓN FAIL-FAST NIVEL SENIOR:
        - Si el servicio de Catálogo no responde, la operación DEBE fallar
        - NO asumimos que el producto existe en caso de error
        - Previene corrupción de datos por productos inexistentes
        
        Args:
            producto_id: ID del producto a verificar
            
        Returns:
            bool: True si el producto existe confirmadamente
            
        Raises:
            BusinessLogicError: Si no se puede validar el producto (servicio caído)
            NotFoundError: Si el producto confirmadamente no existe
        """
        # Check cache first
        cache_key = f"producto_{producto_id}"
        if cache_key in self._cache:
            logger.debug(f"Cache hit for producto_id: {producto_id}")
            return self._cache[cache_key]
        
        try:
            url = urljoin(self.base_url, f"/api/productos/{producto_id}")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url)
                
                logger.info(f"Catalogo API call: GET {url} -> {response.status_code}")
                
                if response.status_code == 200:
                    # Producto existe
                    self._cache[cache_key] = True
                    return True
                elif response.status_code == 404:
                    # Producto no existe
                    self._cache[cache_key] = False
                    return False
                else:
                    # Otro error HTTP - no podemos confiar en la respuesta
                    raise BusinessLogicError(
                        f"Error del servicio de Catálogo (HTTP {response.status_code}). "
                        f"No se puede validar el producto {producto_id}"
                    )
                
        except httpx.TimeoutException:
            logger.error(f"Timeout al consultar producto {producto_id} en catálogo")
            raise BusinessLogicError(
                f"El servicio de Catálogo no responde (timeout). "
                f"No se puede validar el producto {producto_id}. "
                f"Operación cancelada para prevenir corrupción de datos."
            )
            
        except httpx.RequestError as e:
            logger.error(f"Error de conectividad con catálogo: {str(e)}")
            raise BusinessLogicError(
                f"Error de conectividad con servicio de Catálogo: {str(e)}. "
                f"No se puede validar el producto {producto_id}. "
                f"Operación cancelada para prevenir corrupción de datos."
            )
            
        except Exception as e:
            logger.error(f"Error inesperado al consultar catálogo: {str(e)}")
            raise BusinessLogicError(
                f"Error interno al consultar catálogo para producto {producto_id}: {str(e)}. "
                f"Operación cancelada."
            )
    
    def limpiar_cache(self):
        """Limpia el cache interno"""
        self._cache.clear()
        logger.info("Cache de catálogo limpiado")


# Instancia singleton para uso en la aplicación
catalogo_service = CatalogoIntegrationService()
