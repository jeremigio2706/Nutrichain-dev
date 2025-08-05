<?php

namespace CatalogoBundle\Service;

use Doctrine\ORM\EntityManagerInterface;
use Psr\Log\LoggerInterface;
use Symfony\Component\Validator\Validator\ValidatorInterface;
use CatalogoBundle\Entity\Producto;
use CatalogoBundle\Entity\Categoria;
use CatalogoBundle\DTO\ProductoDTO;
use CatalogoBundle\Exception\ValidationException;
use CatalogoBundle\Exception\ProductoNotFoundException;
use CatalogoBundle\Exception\DuplicateSkuException;

/**
 * Servicio para la gestión de productos con DTO unificado y logging comprehensivo
 */
class ProductoService
{
    private $em;
    private $logger;
    private $validator;
    private $repository;

    public function __construct(
        EntityManagerInterface $em, 
        LoggerInterface $logger,
        ValidatorInterface $validator
    ) {
        $this->em = $em;
        $this->logger = $logger;
        $this->validator = $validator;
        $this->repository = $em->getRepository('CatalogoBundle:Producto');
        
        $this->logger->info('ProductoService: Servicio inicializado correctamente');
    }

    /**
     * Obtiene todos los productos con paginación, filtros y búsqueda
     */
    public function obtenerTodos($page = 1, $limit = 20, $filtros = [], $noPagination = false)
    {
        $this->logger->debug('ProductoService::obtenerTodos: Iniciando obtención de productos', [
            'page' => $page,
            'limit' => $limit,
            'filtros' => $filtros,
            'no_pagination' => $noPagination
        ]);

        try {
            $qb = $this->repository->createQueryBuilder('p')
                ->where('p.activo = :activo')
                ->setParameter('activo', true);

            // Aplicar filtros
            if (isset($filtros['categoria']) && !empty($filtros['categoria'])) {
                $qb->andWhere('p.categoria = :categoria')
                   ->setParameter('categoria', $filtros['categoria']);
                
                $this->logger->debug('ProductoService::obtenerTodos: Filtro por categoría aplicado', [
                    'categoria' => $filtros['categoria']
                ]);
            }

            if (isset($filtros['nombre']) && !empty($filtros['nombre'])) {
                $qb->andWhere('LOWER(p.nombre) LIKE :nombre')
                   ->setParameter('nombre', '%' . strtolower($filtros['nombre']) . '%');
                
                $this->logger->debug('ProductoService::obtenerTodos: Filtro por nombre aplicado', [
                    'nombre' => $filtros['nombre']
                ]);
            }

            // Filtro por SKU
            if (isset($filtros['sku']) && !empty($filtros['sku'])) {
                $qb->andWhere('LOWER(p.sku) LIKE :sku')
                   ->setParameter('sku', '%' . strtolower($filtros['sku']) . '%');
                
                $this->logger->debug('ProductoService::obtenerTodos: Filtro por SKU aplicado', [
                    'sku' => $filtros['sku']
                ]);
            }

            // Búsqueda general (nombre, SKU o descripción)
            if (isset($filtros['q']) && !empty($filtros['q'])) {
                $searchTerm = strtolower($filtros['q']);
                $qb->andWhere('(LOWER(p.nombre) LIKE :search OR LOWER(p.sku) LIKE :search OR LOWER(p.descripcion) LIKE :search)')
                   ->setParameter('search', '%' . $searchTerm . '%');
                
                $this->logger->debug('ProductoService::obtenerTodos: Búsqueda general aplicada', [
                    'termino_busqueda' => $filtros['q']
                ]);
            }

            // Contar total con filtros
            $totalQb = clone $qb;
            $total = $totalQb->select('COUNT(p.id)')->getQuery()->getSingleScalarResult();

            // Ordenar por nombre
            $qb->select('p')->orderBy('p.nombre', 'ASC');

            // Aplicar paginación solo si no está deshabilitada
            if (!$noPagination) {
                $qb->setFirstResult(($page - 1) * $limit)
                   ->setMaxResults($limit);
                
                $this->logger->debug('ProductoService::obtenerTodos: Paginación aplicada', [
                    'page' => $page,
                    'limit' => $limit,
                    'offset' => ($page - 1) * $limit
                ]);
            } else {
                $this->logger->debug('ProductoService::obtenerTodos: Sin paginación - obteniendo todos los resultados');
            }

            $productos = $qb->getQuery()->getResult();
            
            $this->logger->info('ProductoService::obtenerTodos: Productos obtenidos exitosamente', [
                'productos_encontrados' => count($productos),
                'total_productos' => $total,
                'page' => $noPagination ? null : $page,
                'limit' => $noPagination ? null : $limit,
                'filtros_aplicados' => $filtros,
                'sin_paginacion' => $noPagination
            ]);

            $resultado = [
                'productos' => $productos,
                'total' => $total
            ];

            // Solo agregar datos de paginación si está habilitada
            if (!$noPagination) {
                $resultado['page'] = $page;
                $resultado['limit'] = $limit;
                $resultado['pages'] = ceil($total / $limit);
            }

            return $resultado;
        } catch (\Exception $e) {
            $this->logger->error('ProductoService::obtenerTodos: Error obteniendo productos', [
                'error_message' => $e->getMessage(),
                'page' => $page,
                'limit' => $limit,
                'filtros' => $filtros,
                'no_pagination' => $noPagination,
                'trace' => $e->getTraceAsString()
            ]);
            throw $e;
        }
    }

    /**
     * Obtiene un producto por ID (por defecto solo activos, pero se puede incluir inactivos)
     */
    public function obtenerPorId($id, $soloActivos = true)
    {
        $this->logger->debug('ProductoService::obtenerPorId: Iniciando búsqueda de producto', [
            'producto_id' => $id,
            'solo_activos' => $soloActivos
        ]);

        try {
            $producto = $this->repository->find($id);
            
            if (!$producto) {
                $this->logger->warning('ProductoService::obtenerPorId: Producto no encontrado', [
                    'producto_id' => $id
                ]);
                throw new ProductoNotFoundException($id);
            }

            // Si solo se buscan activos y el producto está inactivo, considerarlo como no encontrado
            if ($soloActivos && !$producto->getActivo()) {
                $this->logger->warning('ProductoService::obtenerPorId: Producto encontrado pero inactivo', [
                    'producto_id' => $id,
                    'activo' => $producto->getActivo()
                ]);
                throw new ProductoNotFoundException($id);
            }

            $this->logger->info('ProductoService::obtenerPorId: Producto encontrado exitosamente', [
                'producto_id' => $id,
                'producto_nombre' => $producto->getNombre(),
                'producto_sku' => $producto->getSku(),
                'activo' => $producto->getActivo()
            ]);

            return $producto;
        } catch (ProductoNotFoundException $e) {
            throw $e;
        } catch (\Exception $e) {
            $this->logger->error('ProductoService::obtenerPorId: Error obteniendo producto', [
                'producto_id' => $id,
                'error_message' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);
            throw $e;
        }
    }

    /**
     * Crea un nuevo producto usando DTO
     */
    public function crear(ProductoDTO $dto)
    {
        $this->logger->debug('ProductoService::crear: Iniciando creación de producto', [
            'dto_data' => $dto->toArray()
        ]);

        try {
            // Validar que es una operación de creación
            if (!$dto->esCreacion()) {
                $this->logger->warning('ProductoService::crear: DTO incompleto para creación', [
                    'dto_data' => $dto->toArray(),
                    'campos_faltantes' => $this->getCamposFaltantesCreacion($dto)
                ]);
                throw new ValidationException(['general' => 'Faltan campos obligatorios para crear un producto']);
            }

            // Validar DTO
            $errores = $this->validarDTO($dto, true);
            if (!empty($errores)) {
                $this->logger->warning('ProductoService::crear: Errores de validación', [
                    'errores' => $errores,
                    'dto_data' => $dto->toArray()
                ]);
                throw new ValidationException($errores);
            }

            // Verificar que no existe otro producto con el mismo SKU
            if ($this->repository->findOneBy(['sku' => $dto->getSku()])) {
                $this->logger->warning('ProductoService::crear: SKU duplicado', [
                    'sku' => $dto->getSku()
                ]);
                throw new DuplicateSkuException($dto->getSku());
            }

            // Verificar que la categoría existe como string válido
            $categoriasValidas = ['refrigerados', 'secos', 'congelados'];
            if (!in_array($dto->getCategoria(), $categoriasValidas)) {
                $this->logger->warning('ProductoService::crear: Categoría inválida', [
                    'categoria' => $dto->getCategoria(),
                    'categorias_validas' => $categoriasValidas
                ]);
                throw new ValidationException(['categoria' => 'La categoría debe ser: refrigerados, secos o congelados']);
            }

            // Crear la entidad (campos que coinciden con la tabla)
            $producto = new Producto();
            $producto->setNombre($dto->getNombre());
            $producto->setSku($dto->getSku());                    // sku, no codigo
            $producto->setUnidadMedida($dto->getUnidadMedida());
            $producto->setPeso($dto->getPeso());
            $producto->setCategoria($dto->getCategoria());        // string, no entidad
            
            if ($dto->getDescripcion()) {
                $producto->setDescripcion($dto->getDescripcion());
            }
            
            if ($dto->getImagen()) {
                $producto->setImagen($dto->getImagen());
            }

            // Guardar
            $this->em->persist($producto);
            $this->em->flush();

            $this->logger->info('ProductoService::crear: Producto creado exitosamente', [
                'producto_id' => $producto->getId(),
                'producto_nombre' => $producto->getNombre(),
                'producto_sku' => $producto->getSku(),
                'categoria' => $producto->getCategoria()
            ]);

            return $producto;

        } catch (ValidationException $e) {
            throw $e;
        } catch (DuplicateSkuException $e) {
            throw $e;
        } catch (\Exception $e) {
            $this->logger->error('ProductoService::crear: Error creando producto', [
                'dto_data' => $dto->toArray(),
                'error_message' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);
            throw $e;
        }
    }

    /**
     * Actualiza un producto usando DTO
     */
    public function actualizar($id, ProductoDTO $dto)
    {
        $this->logger->debug('ProductoService::actualizar: Iniciando actualización de producto', [
            'producto_id' => $id,
            'dto_data' => $dto->toArray()
        ]);

        try {
            // Obtener el producto existente (incluyendo inactivos para poder reactivarlos)
            $producto = $this->obtenerPorId($id, false);

            // Validar DTO para actualización
            $errores = $this->validarDTO($dto, false);
            if (!empty($errores)) {
                $this->logger->warning('ProductoService::actualizar: Errores de validación', [
                    'producto_id' => $id,
                    'errores' => $errores,
                    'dto_data' => $dto->toArray()
                ]);
                throw new ValidationException($errores);
            }

            $cambios = [];

            // Actualizar campos si están presentes (solo campos que existen en la tabla productos)
            if ($dto->getNombre() !== null) {
                $cambios['nombre'] = ['anterior' => $producto->getNombre(), 'nuevo' => $dto->getNombre()];
                $producto->setNombre($dto->getNombre());
            }

            if ($dto->getSku() !== null) {
                // Verificar duplicados por SKU
                $existente = $this->repository->findOneBy(['sku' => $dto->getSku()]);
                if ($existente && $existente->getId() !== $id) {
                    $this->logger->warning('ProductoService::actualizar: SKU duplicado', [
                        'producto_id' => $id,
                        'sku' => $dto->getSku(),
                        'producto_existente_id' => $existente->getId()
                    ]);
                    throw new DuplicateSkuException($dto->getSku());
                }
                $cambios['sku'] = ['anterior' => $producto->getSku(), 'nuevo' => $dto->getSku()];
                $producto->setSku($dto->getSku());
            }

            if ($dto->getCategoria() !== null) {
                // Verificar que la categoría es válida
                $categoriasValidas = ['refrigerados', 'secos', 'congelados'];
                if (!in_array($dto->getCategoria(), $categoriasValidas)) {
                    throw new ValidationException(['categoria' => 'La categoría debe ser: refrigerados, secos o congelados']);
                }
                $cambios['categoria'] = ['anterior' => $producto->getCategoria(), 'nuevo' => $dto->getCategoria()];
                $producto->setCategoria($dto->getCategoria());
            }

            if ($dto->getUnidadMedida() !== null) {
                $cambios['unidad_medida'] = ['anterior' => $producto->getUnidadMedida(), 'nuevo' => $dto->getUnidadMedida()];
                $producto->setUnidadMedida($dto->getUnidadMedida());
            }

            if ($dto->getPeso() !== null) {
                $cambios['peso'] = ['anterior' => $producto->getPeso(), 'nuevo' => $dto->getPeso()];
                $producto->setPeso($dto->getPeso());
            }

            if ($dto->getDescripcion() !== null) {
                $cambios['descripcion'] = ['anterior' => $producto->getDescripcion(), 'nuevo' => $dto->getDescripcion()];
                $producto->setDescripcion($dto->getDescripcion());
            }

            if ($dto->getImagen() !== null) {
                $cambios['imagen'] = ['anterior' => $producto->getImagen(), 'nuevo' => $dto->getImagen()];
                $producto->setImagen($dto->getImagen());
            }

            if ($dto->getActivo() !== null) {
                $cambios['activo'] = ['anterior' => $producto->getActivo(), 'nuevo' => $dto->getActivo()];
                $producto->setActivo($dto->getActivo());
            }

            $this->em->flush();

            $this->logger->info('ProductoService::actualizar: Producto actualizado exitosamente', [
                'producto_id' => $id,
                'producto_nombre' => $producto->getNombre(),
                'cambios_realizados' => $cambios
            ]);

            return $producto;

        } catch (ProductoNotFoundException $e) {
            throw $e;
        } catch (ValidationException $e) {
            throw $e;
        } catch (DuplicateSkuException $e) {
            throw $e;
        } catch (\Exception $e) {
            $this->logger->error('ProductoService::actualizar: Error actualizando producto', [
                'producto_id' => $id,
                'dto_data' => $dto->toArray(),
                'error_message' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);
            throw $e;
        }
    }

    /**
     * Elimina un producto permanentemente de la base de datos
     */
    public function eliminar($id)
    {
        $this->logger->debug('ProductoService::eliminar: Iniciando eliminación permanente de producto', [
            'producto_id' => $id
        ]);

        try {
            $producto = $this->obtenerPorId($id);

            $this->logger->info('ProductoService::eliminar: Eliminando producto permanentemente de la BD', [
                'producto_id' => $id,
                'producto_nombre' => $producto->getNombre(),
                'producto_sku' => $producto->getSku()
            ]);

            // Eliminación física real de la base de datos
            $this->em->remove($producto);
            $this->em->flush();

            $this->logger->info('ProductoService::eliminar: Producto eliminado permanentemente', [
                'producto_id' => $id,
                'producto_nombre' => $producto->getNombre(),
                'producto_sku' => $producto->getSku()
            ]);

            return true;

        } catch (ProductoNotFoundException $e) {
            throw $e;
        } catch (\Exception $e) {
            $this->logger->error('ProductoService::eliminar: Error eliminando producto permanentemente', [
                'producto_id' => $id,
                'error_message' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);
            throw $e;
        }
    }

    /**
     * Valida un DTO de producto
     */
    private function validarDTO(ProductoDTO $dto, $esCreacion = false)
    {
        $errores = [];

        // Para creación, validar campos obligatorios
        if ($esCreacion) {
            if (!$dto->getNombre()) {
                $errores['nombre'] = 'El nombre es obligatorio';
            }
            if (!$dto->getSku()) {
                $errores['sku'] = 'El SKU es obligatorio';
            }
            if (!$dto->getCategoria()) {
                $errores['categoria'] = 'La categoría es obligatoria';
            }
            if (!$dto->getUnidadMedida()) {
                $errores['unidad_medida'] = 'La unidad de medida es obligatoria';
            }
            if (!$dto->getPeso() || $dto->getPeso() <= 0) {
                $errores['peso'] = 'El peso es obligatorio y debe ser mayor a cero';
            }
        }

        // Usar el validador de Symfony
        $violations = $this->validator->validate($dto);
        foreach ($violations as $violation) {
            $campo = $violation->getPropertyPath();
            if (!isset($errores[$campo])) {
                $errores[$campo] = [];
            }
            $errores[$campo][] = $violation->getMessage();
        }

        return $errores;
    }

    /**
     * Obtiene los campos faltantes para una creación
     */
    private function getCamposFaltantesCreacion(ProductoDTO $dto)
    {
        $faltantes = [];
        
        if (!$dto->getNombre()) $faltantes[] = 'nombre';
        if (!$dto->getSku()) $faltantes[] = 'sku';
        if (!$dto->getCategoria()) $faltantes[] = 'categoria';
        if (!$dto->getUnidadMedida()) $faltantes[] = 'unidad_medida';
        if (!$dto->getPeso() || $dto->getPeso() <= 0) $faltantes[] = 'peso';
        
        return $faltantes;
    }
}
