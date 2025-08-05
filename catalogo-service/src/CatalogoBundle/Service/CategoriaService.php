<?php

namespace CatalogoBundle\Service;

use Doctrine\ORM\EntityManagerInterface;
use Psr\Log\LoggerInterface;
use Symfony\Component\Validator\Validator\ValidatorInterface;
use CatalogoBundle\Entity\Categoria;
use CatalogoBundle\DTO\CategoriaDTO;
use CatalogoBundle\Exception\ValidationException;
use CatalogoBundle\Exception\CategoriaNotFoundException;
use CatalogoBundle\Exception\DuplicateCodigoCategoriaException;
use CatalogoBundle\Repository\CategoriaRepository;

class CategoriaService
{
    private $em;
    private $logger;
    private $repository;
    private $validator;

    public function __construct(
        EntityManagerInterface $em,
        LoggerInterface $logger,
        ValidatorInterface $validator
    ) {
        $this->em = $em;
        $this->logger = $logger;
        $this->validator = $validator;
        $this->repository = $em->getRepository(Categoria::class);
    }

    public function obtenerTodas(): array
    {
        $this->logger->info('CategoriaService: Iniciando obtenerTodas()');
        
        try {
            // Verificar que el repositorio se inicializó correctamente
            if (!$this->repository) {
                $this->logger->error('CategoriaService: Repository no está inicializado');
                throw new \RuntimeException('Repository no está inicializado');
            }
            
            $this->logger->info('CategoriaService: Buscando categorías activas en BD');
            
            // Usamos el nombre de la propiedad 'activo', no 'activa'
            $categorias = $this->repository->findBy(['activo' => true], ['nombre' => 'ASC']);
            
            $this->logger->info('CategoriaService: Categorías encontradas', [
                'total_categorias' => count($categorias),
                'repository_class' => get_class($this->repository)
            ]);
            
            return $categorias;
        } catch (\Exception $e) {
            $this->logger->error('CategoriaService: Error en obtenerTodas()', [
                'error_message' => $e->getMessage(),
                'error_class' => get_class($e),
                'error_file' => $e->getFile(),
                'error_line' => $e->getLine()
            ]);
            throw $e;
        }
    }

    public function obtenerPorId(int $id, bool $soloActivos = true): Categoria
    {
        $this->logger->info('CategoriaService: Iniciando obtenerPorId()', [
            'categoria_id' => $id,
            'solo_activos' => $soloActivos
        ]);
        
        try {
            $categoria = $this->repository->find($id);
            
            if (!$categoria) {
                $this->logger->warning('CategoriaService: Categoría no encontrada en BD', ['categoria_id' => $id]);
                throw CategoriaNotFoundException::forId($id);
            }
            
            // Si solo se buscan activos y la categoría está inactiva, considerarla como no encontrada
            if ($soloActivos && !$categoria->isActivo()) {
                $this->logger->warning('CategoriaService: Categoría encontrada pero inactiva', [
                    'categoria_id' => $id,
                    'activo' => $categoria->isActivo()
                ]);
                throw CategoriaNotFoundException::forId($id);
            }
            
            $this->logger->info('CategoriaService: Categoría encontrada exitosamente', [
                'categoria_id' => $id,
                'categoria_codigo' => $categoria->getCodigo(),
                'categoria_nombre' => $categoria->getNombre(),
                'activo' => $categoria->isActivo()
            ]);
            
            return $categoria;
        } catch (\Exception $e) {
            $this->logger->error('CategoriaService: Error en obtenerPorId()', [
                'categoria_id' => $id,
                'error_message' => $e->getMessage(),
                'error_class' => get_class($e)
            ]);
            throw $e;
        }
    }

    public function crear(CategoriaDTO $dto): Categoria
    {
        $this->logger->info('CategoriaService: Iniciando crear()', [
            'dto_codigo' => $dto->codigo,
            'dto_nombre' => $dto->nombre
        ]);
        
        try {
            $this->logger->info('CategoriaService: Validando DTO para creación');
            $this->validateDto($dto, ['create', 'Default']);
            
            $this->logger->info('CategoriaService: Verificando que el código no exista', [
                'codigo' => $dto->codigo
            ]);
            
            if ($this->repository->existeCodigo($dto->codigo)) {
                $this->logger->warning('CategoriaService: Código ya existe en BD', [
                    'codigo' => $dto->codigo
                ]);
                throw new DuplicateCodigoCategoriaException($dto->codigo);
            }

            $this->logger->info('CategoriaService: Creando nueva entidad Categoria');
            $categoria = new Categoria();
            $this->mapearDtoAEntidad($dto, $categoria);

            $this->logger->info('CategoriaService: Persistiendo categoría en BD');
            $this->em->persist($categoria);
            $this->em->flush();

            $this->logger->info('CategoriaService: Categoría creada exitosamente', [
                'id' => $categoria->getId(),
                'codigo' => $categoria->getCodigo(),
                'nombre' => $categoria->getNombre()
            ]);
            
            return $categoria;
        } catch (\Exception $e) {
            $this->logger->error('CategoriaService: Error en crear()', [
                'dto_codigo' => $dto->codigo,
                'dto_nombre' => $dto->nombre,
                'error_message' => $e->getMessage(),
                'error_class' => get_class($e)
            ]);
            throw $e;
        }
    }

    public function actualizar(int $id, CategoriaDTO $dto): Categoria
    {
        $this->logger->info('CategoriaService: Iniciando actualizar()', [
            'categoria_id' => $id,
            'dto_codigo' => $dto->codigo,
            'dto_nombre' => $dto->nombre
        ]);
        
        try {
            $this->logger->info('CategoriaService: Validando DTO para actualización');
            $this->validateDto($dto, ['update', 'Default']);
            
            $this->logger->info('CategoriaService: Obteniendo categoría existente (incluyendo inactivas)');
            $categoria = $this->obtenerPorId($id, false);

            // Verificar código duplicado solo si se está cambiando
            if ($dto->codigo && $dto->codigo !== $categoria->getCodigo()) {
                $this->logger->info('CategoriaService: Verificando nuevo código', [
                    'codigo_anterior' => $categoria->getCodigo(),
                    'codigo_nuevo' => $dto->codigo
                ]);
                
                if ($this->repository->existeCodigo($dto->codigo)) {
                    $this->logger->warning('CategoriaService: Nuevo código ya existe', [
                        'codigo_nuevo' => $dto->codigo
                    ]);
                    throw new DuplicateCodigoCategoriaException($dto->codigo);
                }
            }

            $this->logger->info('CategoriaService: Mapeando datos del DTO a la entidad');
            $this->mapearDtoAEntidad($dto, $categoria);
            
            $this->em->flush();
            
            $this->logger->info('CategoriaService: Categoría actualizada exitosamente', [
                'id' => $id,
                'codigo' => $categoria->getCodigo(),
                'nombre' => $categoria->getNombre()
            ]);
            
            return $categoria;
        } catch (\Exception $e) {
            $this->logger->error('CategoriaService: Error en actualizar()', [
                'categoria_id' => $id,
                'dto_codigo' => $dto->codigo,
                'error_message' => $e->getMessage(),
                'error_class' => get_class($e)
            ]);
            throw $e;
        }
    }

    public function eliminar(int $id): void
    {
        $this->logger->info('CategoriaService: Iniciando eliminación permanente', ['categoria_id' => $id]);
        
        try {
            $this->logger->info('CategoriaService: Obteniendo categoría para eliminar');
            $categoria = $this->obtenerPorId($id);

            $this->logger->info('CategoriaService: Verificando productos asociados');
            
            $productosRepository = $this->em->getRepository('CatalogoBundle:Producto');
            $countProductos = $productosRepository->createQueryBuilder('p')
                ->select('COUNT(p.id)')
                ->where('p.categoria = :categoria')
                ->andWhere('p.activo = :activo')
                ->setParameter('categoria', $categoria->getCodigo())
                ->setParameter('activo', true)
                ->getQuery()
                ->getSingleScalarResult();
            
            if ($countProductos > 0) {
                $this->logger->warning('CategoriaService: No se puede eliminar categoría con productos activos', [
                    'categoria_id' => $id,
                    'categoria_codigo' => $categoria->getCodigo(),
                    'productos_asociados' => $countProductos
                ]);
                throw new ValidationException(['general' => 'No se puede eliminar la categoría porque tiene productos activos asociados.']);
            }

            $this->logger->info('CategoriaService: Eliminando categoría permanentemente de la BD', [
                'categoria_id' => $id,
                'categoria_codigo' => $categoria->getCodigo(),
                'categoria_nombre' => $categoria->getNombre()
            ]);

            // Eliminación física real de la base de datos
            $this->em->remove($categoria);
            $this->em->flush();
            
            $this->logger->info('CategoriaService: Categoría eliminada permanentemente', [
                'id' => $id,
                'codigo' => $categoria->getCodigo(),
                'nombre' => $categoria->getNombre()
            ]);
        } catch (\Exception $e) {
            $this->logger->error('CategoriaService: Error en eliminación permanente', [
                'categoria_id' => $id,
                'error_message' => $e->getMessage(),
                'error_class' => get_class($e)
            ]);
            throw $e;
        }
    }

    private function mapearDtoAEntidad(CategoriaDTO $dto, Categoria $categoria): void
    {
        $this->logger->debug('CategoriaService: Iniciando mapeo DTO a entidad', [
            'dto_campos_definidos' => [
                'nombre' => $dto->nombre !== null,
                'codigo' => $dto->codigo !== null,
                'descripcion' => $dto->descripcion !== null,
                'temperaturaMin' => $dto->temperaturaMin !== null,
                'temperaturaMax' => $dto->temperaturaMax !== null,
                'activo' => $dto->activo !== null
            ]
        ]);
        
        if ($dto->nombre !== null) {
            $categoria->setNombre($dto->nombre);
            $this->logger->debug('CategoriaService: Nombre mapeado', ['nombre' => $dto->nombre]);
        }
        if ($dto->codigo !== null) {
            $categoria->setCodigo($dto->codigo);
            $this->logger->debug('CategoriaService: Código mapeado', ['codigo' => $dto->codigo]);
        }
        if ($dto->descripcion !== null) {
            $categoria->setDescripcion($dto->descripcion);
            $this->logger->debug('CategoriaService: Descripción mapeada');
        }
        if ($dto->temperaturaMin !== null) {
            $categoria->setTemperaturaMin($dto->temperaturaMin);
            $this->logger->debug('CategoriaService: Temperatura mínima mapeada', ['temp_min' => $dto->temperaturaMin]);
        }
        if ($dto->temperaturaMax !== null) {
            $categoria->setTemperaturaMax($dto->temperaturaMax);
            $this->logger->debug('CategoriaService: Temperatura máxima mapeada', ['temp_max' => $dto->temperaturaMax]);
        }
        if ($dto->activo !== null) {
            $categoria->setActivo($dto->activo);
            $this->logger->debug('CategoriaService: Estado activo mapeado', ['activo' => $dto->activo]);
        }
        
        $this->logger->debug('CategoriaService: Mapeo DTO a entidad completado');
    }

    private function validateDto($dto, array $groups): void
    {
        $this->logger->debug('CategoriaService: Iniciando validación de DTO', [
            'validation_groups' => $groups,
            'dto_class' => get_class($dto)
        ]);
        
        $violations = $this->validator->validate($dto, null, $groups);
        
        if (count($violations) > 0) {
            $errors = [];
            foreach ($violations as $violation) {
                $errors[$violation->getPropertyPath()][] = $violation->getMessage();
            }
            
            $this->logger->warning('CategoriaService: Errores de validación encontrados', [
                'violation_count' => count($violations),
                'errors' => $errors
            ]);
            
            throw new ValidationException($errors);
        }
        
        $this->logger->debug('CategoriaService: Validación de DTO exitosa');
    }
}
