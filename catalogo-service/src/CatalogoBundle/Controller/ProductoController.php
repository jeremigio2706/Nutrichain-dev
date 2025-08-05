<?php

namespace CatalogoBundle\Controller;

use FOS\RestBundle\Controller\FOSRestController;
use FOS\RestBundle\Controller\Annotations as Rest;
use FOS\RestBundle\View\View;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Nelmio\ApiDocBundle\Annotation\ApiDoc;
use CatalogoBundle\DTO\ProductoDTO;
use CatalogoBundle\Exception\ValidationException;
use CatalogoBundle\Exception\ProductoNotFoundException;
use CatalogoBundle\Exception\DuplicateSkuException;

/**
 * Controlador para la gestión de productos
 * 
 * @Rest\Route("/productos")
 */
class ProductoController extends FOSRestController
{
    /**
     * Lista productos con paginación y filtros
     *
     * @ApiDoc(
     *     description="Obtiene una lista de productos activos con filtros opcionales y paginación configurable",
     *     section="Productos",
     *     parameters={
     *         {"name"="page", "dataType"="integer", "required"=false, "description"="Número de página (por defecto: 1)"},
     *         {"name"="limit", "dataType"="integer", "required"=false, "description"="Productos por página (por defecto: 20, máximo: 100)"},
     *         {"name"="no_pagination", "dataType"="boolean", "required"=false, "description"="true para obtener todos los productos sin paginación"},
     *         {"name"="nombre", "dataType"="string", "required"=false, "description"="Filtrar por nombre del producto"},
     *         {"name"="categoria", "dataType"="string", "required"=false, "description"="Filtrar por categoría (refrigerados, secos, congelados)"},
     *         {"name"="sku", "dataType"="string", "required"=false, "description"="Filtrar por SKU del producto"},
     *         {"name"="q", "dataType"="string", "required"=false, "description"="Búsqueda general en nombre, SKU y descripción"}
     *     },
     *     statusCodes={
     *         200="Devuelve la lista de productos",
     *         500="Error interno del servidor"
     *     }
     * )
     * @Rest\Get("")
     * @Rest\View(serializerGroups={"producto_list"})
     */
    public function listAction(Request $request)
    {
        try {
            // Parámetros de paginación
            $noPagination = $request->query->getBoolean('no_pagination', false);
            $page = $noPagination ? 1 : max(1, $request->query->getInt('page', 1));
            $limit = $noPagination ? 20 : min(100, max(1, $request->query->getInt('limit', 20)));

            // Obtener filtros de la query string
            $filtros = [];
            if ($nombre = $request->query->get('nombre')) {
                $filtros['nombre'] = $nombre;
            }
            if ($categoria = $request->query->get('categoria')) {
                $filtros['categoria'] = $categoria;
            }
            if ($sku = $request->query->get('sku')) {
                $filtros['sku'] = $sku;
            }
            if ($q = $request->query->get('q')) {
                $filtros['q'] = $q;
            }

            $productoService = $this->get('catalogo.service.producto');
            
            // Usar obtenerTodos con filtros y opción de paginación
            $resultado = $productoService->obtenerTodos($page, $limit, $filtros, $noPagination);

            $response = [
                'success' => true,
                'data' => $resultado['productos'],
                'total' => $resultado['total']
            ];

            // Solo agregar paginación si está habilitada
            if (!$noPagination) {
                $response['pagination'] = [
                    'page' => $resultado['page'],
                    'limit' => $resultado['limit'],
                    'pages' => $resultado['pages']
                ];
            }

            // Si hay filtros, incluir información de búsqueda
            if (!empty($filtros)) {
                $response['filters'] = $filtros;
            }

            return $this->view($response, Response::HTTP_OK);

        } catch (\Exception $e) {
            return $this->handleException($e, 'Error al obtener productos');
        }
    }

    /**
     * Obtiene un producto específico por ID
     *
     * @ApiDoc(
     *     description="Obtiene los detalles de un producto específico",
     *     section="Productos",
     *     requirements={
     *         {"name"="id", "dataType"="integer", "required"=true, "description"="ID del producto"}
     *     },
     *     statusCodes={
     *         200="Devuelve los datos del producto",
     *         404="Producto no encontrado",
     *         500="Error interno del servidor"
     *     }
     * )
     * @Rest\Get("/{id}")
     * @Rest\View(serializerGroups={"producto_detail"})
     */
    public function getAction($id)
    {
        try {
            $productoService = $this->get('catalogo.service.producto');
            $producto = $productoService->obtenerPorId($id);

            return $this->view([
                'success' => true,
                'data' => $producto
            ], Response::HTTP_OK);

        } catch (ProductoNotFoundException $e) {
            return $this->view([
                'success' => false,
                'message' => 'Producto no encontrado',
                'error' => $e->getMessage()
            ], Response::HTTP_NOT_FOUND);
        } catch (\Exception $e) {
            return $this->view([
                'success' => false,
                'message' => 'Error al obtener producto',
                'error' => $e->getMessage()
            ], Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }

    /**
     * Crea un nuevo producto
     *
     * @ApiDoc(
     *     description="Crea un nuevo producto",
     *     section="Productos",
     *     input="array",
     *     parameters={
     *         {"name"="nombre", "dataType"="string", "required"=true, "description"="Nombre del producto"},
     *         {"name"="sku", "dataType"="string", "required"=true, "description"="SKU único del producto"},
     *         {"name"="categoria", "dataType"="string", "required"=true, "description"="Categoría del producto (refrigerados, secos, congelados)"},
     *         {"name"="unidad_medida", "dataType"="string", "required"=true, "description"="Unidad de medida (kg, litro, unidad, docena)"},
     *         {"name"="peso", "dataType"="float", "required"=true, "description"="Peso del producto en gramos"},
     *         {"name"="descripcion", "dataType"="string", "required"=false, "description"="Descripción del producto"},
     *         {"name"="imagen", "dataType"="string", "required"=false, "description"="URL de la imagen del producto (jpg, jpeg, png, gif, webp)"}
     *     },
     *     statusCodes={
     *         201="Producto creado exitosamente",
     *         400="Datos de entrada inválidos",
     *         409="SKU duplicado",
     *         500="Error interno del servidor"
     *     }
     * )
     * @Rest\Post("")
     * @Rest\View(serializerGroups={"producto_detail"})
     */
    public function createAction(Request $request)
    {
        try {
            $datos = json_decode($request->getContent(), true);

            if (!$datos) {
                return $this->view([
                    'success' => false,
                    'message' => 'Datos JSON inválidos'
                ], Response::HTTP_BAD_REQUEST);
            }

            // Validar imagen antes de enviar al servicio
            $errorImagen = $this->validarImagen($datos);
            if ($errorImagen) {
                return $this->view($errorImagen, Response::HTTP_BAD_REQUEST);
            }

            // Crear DTO desde los datos
            $dto = new \CatalogoBundle\DTO\ProductoDTO();
            if (isset($datos['nombre'])) $dto->setNombre($datos['nombre']);
            if (isset($datos['sku'])) $dto->setSku($datos['sku']);
            if (isset($datos['categoria'])) $dto->setCategoria($datos['categoria']);
            if (isset($datos['unidad_medida'])) $dto->setUnidadMedida($datos['unidad_medida']);
            if (isset($datos['peso'])) $dto->setPeso($datos['peso']);
            if (isset($datos['descripcion'])) $dto->setDescripcion($datos['descripcion']);
            if (isset($datos['imagen'])) $dto->setImagen($datos['imagen']);

            $productoService = $this->get('catalogo.service.producto');
            $producto = $productoService->crear($dto);

            return $this->view([
                'success' => true,
                'message' => 'Producto creado exitosamente',
                'data' => $producto
            ], Response::HTTP_CREATED);

        } catch (ValidationException $e) {
            return $this->view([
                'success' => false,
                'message' => 'Error de validación',
                'error' => $e->getMessage(),
                'errors' => $e->getErrors()
            ], Response::HTTP_BAD_REQUEST);
        } catch (DuplicateSkuException $e) {
            return $this->view([
                'success' => false,
                'message' => 'SKU duplicado',
                'error' => $e->getMessage()
            ], Response::HTTP_CONFLICT);
        } catch (\Exception $e) {
            return $this->view([
                'success' => false,
                'message' => 'Error interno del servidor',
                'error' => $e->getMessage()
            ], Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }

    /**
     * Actualiza un producto existente
     *
     * @ApiDoc(
     *     description="Actualiza un producto existente. Solo se actualizan los campos enviados.",
     *     section="Productos",
     *     requirements={
     *         {"name"="id", "dataType"="integer", "required"=true, "description"="ID del producto"}
     *     },
     *     input="array",
     *     parameters={
     *         {"name"="nombre", "dataType"="string", "required"=false, "description"="Nombre del producto"},
     *         {"name"="sku", "dataType"="string", "required"=false, "description"="SKU único del producto"},
     *         {"name"="categoria", "dataType"="string", "required"=false, "description"="Categoría del producto (refrigerados, secos, congelados)"},
     *         {"name"="unidad_medida", "dataType"="string", "required"=false, "description"="Unidad de medida (kg, litro, unidad, docena)"},
     *         {"name"="peso", "dataType"="float", "required"=false, "description"="Peso del producto en gramos"},
     *         {"name"="descripcion", "dataType"="string", "required"=false, "description"="Descripción del producto"},
     *         {"name"="imagen", "dataType"="string", "required"=false, "description"="URL de la imagen del producto (jpg, jpeg, png, gif, webp)"},
     *         {"name"="activo", "dataType"="boolean", "required"=false, "description"="Estado del producto (true=activo, false=inactivo)"}
     *     },
     *     statusCodes={
     *         200="Producto actualizado exitosamente",
     *         400="Datos de entrada inválidos",
     *         404="Producto no encontrado",
     *         409="SKU duplicado",
     *         500="Error interno del servidor"
     *     }
     * )
     * @Rest\Put("/{id}")
     * @Rest\View(serializerGroups={"producto_detail"})
     */
    public function updateAction($id, Request $request)
    {
        try {
            $datos = json_decode($request->getContent(), true);

            if (!$datos) {
                return $this->view([
                    'success' => false,
                    'message' => 'Datos JSON inválidos'
                ], Response::HTTP_BAD_REQUEST);
            }

            // Validar imagen antes de enviar al servicio
            $errorImagen = $this->validarImagen($datos);
            if ($errorImagen) {
                return $this->view($errorImagen, Response::HTTP_BAD_REQUEST);
            }

            // Crear DTO desde los datos (solo campos presentes)
            $dto = new \CatalogoBundle\DTO\ProductoDTO();
            if (isset($datos['nombre'])) $dto->setNombre($datos['nombre']);
            if (isset($datos['sku'])) $dto->setSku($datos['sku']);
            if (isset($datos['categoria'])) $dto->setCategoria($datos['categoria']);
            if (isset($datos['unidad_medida'])) $dto->setUnidadMedida($datos['unidad_medida']);
            if (isset($datos['peso'])) $dto->setPeso($datos['peso']);
            if (isset($datos['descripcion'])) $dto->setDescripcion($datos['descripcion']);
            if (isset($datos['imagen'])) $dto->setImagen($datos['imagen']);
            if (isset($datos['activo'])) $dto->setActivo($datos['activo']);

            $productoService = $this->get('catalogo.service.producto');
            $producto = $productoService->actualizar($id, $dto);

            return $this->view([
                'success' => true,
                'message' => 'Producto actualizado exitosamente',
                'data' => $producto
            ], Response::HTTP_OK);

        } catch (ValidationException $e) {
            return $this->view([
                'success' => false,
                'message' => 'Error de validación',
                'error' => $e->getMessage(),
                'errors' => $e->getErrors()
            ], Response::HTTP_BAD_REQUEST);
        } catch (ProductoNotFoundException $e) {
            return $this->view([
                'success' => false,
                'message' => 'Producto no encontrado',
                'error' => $e->getMessage()
            ], Response::HTTP_NOT_FOUND);
        } catch (DuplicateSkuException $e) {
            return $this->view([
                'success' => false,
                'message' => 'SKU duplicado',
                'error' => $e->getMessage()
            ], Response::HTTP_CONFLICT);
        } catch (\Exception $e) {
            return $this->view([
                'success' => false,
                'message' => 'Error interno del servidor',
                'error' => $e->getMessage()
            ], Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }

    /**
     * Elimina un producto permanentemente de la base de datos
     *
     * @ApiDoc(
     *     description="Elimina un producto permanentemente de la base de datos. Para desactivar un producto use PUT con activo=false.",
     *     section="Productos",
     *     requirements={
     *         {"name"="id", "dataType"="integer", "required"=true, "description"="ID del producto"}
     *     },
     *     statusCodes={
     *         200="Producto eliminado exitosamente",
     *         404="Producto no encontrado",
     *         500="Error interno del servidor"
     *     }
     * )
     * @Rest\Delete("/{id}")
     */
    public function deleteAction($id)
    {
        try {
            $productoService = $this->get('catalogo.service.producto');
            $resultado = $productoService->eliminar($id);

            return $this->view([
                'success' => true,
                'message' => 'Producto eliminado exitosamente'
            ], Response::HTTP_OK);

        } catch (ProductoNotFoundException $e) {
            return $this->view([
                'success' => false,
                'message' => 'Producto no encontrado',
                'error' => $e->getMessage()
            ], Response::HTTP_NOT_FOUND);
        } catch (\Exception $e) {
            return $this->view([
                'success' => false,
                'message' => 'Error al eliminar producto',
                'error' => $e->getMessage()
            ], Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }

    /**
     * Maneja las excepciones de manera consistente
     *
     * @param \Exception $e
     * @param string $defaultMessage
     * @return View
     */
    private function handleException(\Exception $e, string $defaultMessage = 'Error interno'): View
    {
        $this->get('logger')->error($defaultMessage . ': ' . $e->getMessage());

        if ($e instanceof ValidationException) {
            return $this->view([
                'success' => false,
                'message' => 'Errores de validación',
                'errors' => $e->getFormattedErrors()
            ], Response::HTTP_BAD_REQUEST);
        }

        if ($e instanceof ProductoNotFoundException) {
            return $this->view([
                'success' => false,
                'message' => $e->getMessage()
            ], Response::HTTP_NOT_FOUND);
        }

        if ($e instanceof DuplicateSkuException) {
            return $this->view([
                'success' => false,
                'message' => $e->getMessage()
            ], Response::HTTP_CONFLICT);
        }

        return $this->view([
            'success' => false,
            'message' => $defaultMessage,
            'error' => $e->getMessage()
        ], Response::HTTP_INTERNAL_SERVER_ERROR);
    }

    /**
     * Valida que los datos contengan una imagen válida
     *
     * @param array $datos
     * @return array|null Array con error si la validación falla, null si es válida
     */
    private function validarImagen(array $datos): ?array
    {
        if (!isset($datos['imagen']) || empty($datos['imagen'])) {
            return null; // La imagen es opcional
        }

        $imagen = $datos['imagen'];

        // Verificar que sea una URL válida
        if (!filter_var($imagen, FILTER_VALIDATE_URL)) {
            return [
                'success' => false,
                'message' => 'Error de validación de imagen',
                'error' => 'La imagen debe ser una URL válida',
                'field' => 'imagen'
            ];
        }

        $urlParts = parse_url($imagen);
        
        // Verificar protocolo
        if (!isset($urlParts['scheme']) || !in_array($urlParts['scheme'], ['http', 'https'])) {
            return [
                'success' => false,
                'message' => 'Error de validación de imagen',
                'error' => 'La imagen debe usar protocolo HTTP o HTTPS',
                'field' => 'imagen'
            ];
        }

        // Verificar extensión de imagen
        $path = $urlParts['path'] ?? '';
        $extension = strtolower(pathinfo($path, PATHINFO_EXTENSION));
        $extensionesValidas = ['jpg', 'jpeg', 'png', 'gif', 'webp'];
        
        if (empty($extension) || !in_array($extension, $extensionesValidas)) {
            return [
                'success' => false,
                'message' => 'Error de validación de imagen',
                'error' => 'La imagen debe tener una extensión válida (jpg, jpeg, png, gif, webp)',
                'field' => 'imagen',
                'allowed_extensions' => $extensionesValidas
            ];
        }

        // Verificar host válido
        $host = $urlParts['host'] ?? '';
        if (empty($host)) {
            return [
                'success' => false,
                'message' => 'Error de validación de imagen',
                'error' => 'La imagen debe tener un dominio válido',
                'field' => 'imagen'
            ];
        }

        return null; // Validación exitosa
    }
}
