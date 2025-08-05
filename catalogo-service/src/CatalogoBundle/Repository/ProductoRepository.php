<?php

namespace CatalogoBundle\Repository;

use Doctrine\ORM\EntityRepository;
use Doctrine\ORM\Query;

/**
 * Repository para entidad Producto
 */
class ProductoRepository extends EntityRepository
{
    /**
     * Obtiene todos los productos activos con paginación
     *
     * @param int $page
     * @param int $limit
     * @return array
     */
    public function findActivosPaginados($page = 1, $limit = 20)
    {
        $query = $this->createQueryBuilder('p')
            ->where('p.activo = :activo')
            ->setParameter('activo', true)
            ->orderBy('p.nombre', 'ASC')
            ->getQuery();

        $query->setFirstResult(($page - 1) * $limit)
              ->setMaxResults($limit);

        return $query->getResult();
    }

    /**
     * Cuenta todos los productos activos
     *
     * @return int
     */
    public function countActivos()
    {
        return $this->createQueryBuilder('p')
            ->select('COUNT(p.id)')
            ->where('p.activo = :activo')
            ->setParameter('activo', true)
            ->getQuery()
            ->getSingleScalarResult();
    }

    /**
     * Busca productos por nombre
     *
     * @param string $nombre
     * @param int $page
     * @param int $limit
     * @return array
     */
    public function findByNombre($nombre, $page = 1, $limit = 20)
    {
        $query = $this->createQueryBuilder('p')
            ->where('p.nombre LIKE :nombre')
            ->andWhere('p.activo = :activo')
            ->setParameter('nombre', '%' . $nombre . '%')
            ->setParameter('activo', true)
            ->orderBy('p.nombre', 'ASC')
            ->getQuery();

        $query->setFirstResult(($page - 1) * $limit)
              ->setMaxResults($limit);

        return $query->getResult();
    }

    /**
     * Busca productos por categoría
     *
     * @param string $categoria
     * @param int $page
     * @param int $limit
     * @return array
     */
    public function findByCategoria($categoria, $page = 1, $limit = 20)
    {
        $query = $this->createQueryBuilder('p')
            ->where('p.categoria = :categoria')
            ->andWhere('p.activo = :activo')
            ->setParameter('categoria', $categoria)
            ->setParameter('activo', true)
            ->orderBy('p.nombre', 'ASC')
            ->getQuery();

        $query->setFirstResult(($page - 1) * $limit)
              ->setMaxResults($limit);

        return $query->getResult();
    }

    /**
     * Busca productos por SKU
     *
     * @param string $sku
     * @return Producto|null
     */
    public function findBySku($sku)
    {
        return $this->createQueryBuilder('p')
            ->where('p.sku = :sku')
            ->andWhere('p.activo = :activo')
            ->setParameter('sku', $sku)
            ->setParameter('activo', true)
            ->getQuery()
            ->getOneOrNullResult();
    }

    /**
     * Verifica si existe un producto con el SKU dado
     *
     * @param string $sku
     * @param int|null $excludeId
     * @return bool
     */
    public function existeSku($sku, $excludeId = null)
    {
        $qb = $this->createQueryBuilder('p')
            ->select('COUNT(p.id)')
            ->where('p.sku = :sku')
            ->setParameter('sku', $sku);

        if ($excludeId) {
            $qb->andWhere('p.id != :excludeId')
               ->setParameter('excludeId', $excludeId);
        }

        return $qb->getQuery()->getSingleScalarResult() > 0;
    }

    /**
     * Obtiene productos con bajo stock (menos de X unidades)
     * Nota: Esta función está preparada para futuras implementaciones de inventario
     *
     * @param int $limite
     * @return array
     */
    public function findBajoStock($limite = 10)
    {
        // Por ahora retorna productos activos, se puede expandir cuando se implemente inventario
        return $this->createQueryBuilder('p')
            ->where('p.activo = :activo')
            ->setParameter('activo', true)
            ->orderBy('p.nombre', 'ASC')
            ->setMaxResults($limite)
            ->getQuery()
            ->getResult();
    }

    /**
     * Busca productos con filtros múltiples
     *
     * @param array $filtros
     * @param int $page
     * @param int $limit
     * @return array
     */
    public function findConFiltros($filtros = [], $page = 1, $limit = 20)
    {
        $qb = $this->createQueryBuilder('p')
            ->where('p.activo = :activo')
            ->setParameter('activo', true);

        if (!empty($filtros['nombre'])) {
            $qb->andWhere('p.nombre LIKE :nombre')
               ->setParameter('nombre', '%' . $filtros['nombre'] . '%');
        }

        if (!empty($filtros['categoria'])) {
            $qb->andWhere('p.categoria = :categoria')
               ->setParameter('categoria', $filtros['categoria']);
        }

        if (!empty($filtros['sku'])) {
            $qb->andWhere('p.sku LIKE :sku')
               ->setParameter('sku', '%' . $filtros['sku'] . '%');
        }

        if (isset($filtros['peso_min'])) {
            $qb->andWhere('p.peso >= :peso_min')
               ->setParameter('peso_min', $filtros['peso_min']);
        }

        if (isset($filtros['peso_max'])) {
            $qb->andWhere('p.peso <= :peso_max')
               ->setParameter('peso_max', $filtros['peso_max']);
        }

        $qb->orderBy('p.nombre', 'ASC');

        $query = $qb->getQuery();
        $query->setFirstResult(($page - 1) * $limit)
              ->setMaxResults($limit);

        return $query->getResult();
    }

    /**
     * Cuenta productos con filtros aplicados
     *
     * @param array $filtros
     * @return int
     */
    public function countConFiltros($filtros = [])
    {
        $qb = $this->createQueryBuilder('p')
            ->select('COUNT(p.id)')
            ->where('p.activo = :activo')
            ->setParameter('activo', true);

        if (!empty($filtros['nombre'])) {
            $qb->andWhere('p.nombre LIKE :nombre')
               ->setParameter('nombre', '%' . $filtros['nombre'] . '%');
        }

        if (!empty($filtros['categoria'])) {
            $qb->andWhere('p.categoria = :categoria')
               ->setParameter('categoria', $filtros['categoria']);
        }

        if (!empty($filtros['sku'])) {
            $qb->andWhere('p.sku LIKE :sku')
               ->setParameter('sku', '%' . $filtros['sku'] . '%');
        }

        if (isset($filtros['peso_min'])) {
            $qb->andWhere('p.peso >= :peso_min')
               ->setParameter('peso_min', $filtros['peso_min']);
        }

        if (isset($filtros['peso_max'])) {
            $qb->andWhere('p.peso <= :peso_max')
               ->setParameter('peso_max', $filtros['peso_max']);
        }

        return $qb->getQuery()->getSingleScalarResult();
    }

    /**
     * Obtiene estadísticas básicas de productos
     *
     * @return array
     */
    public function getEstadisticas()
    {
        $total = $this->countActivos();
        
        $porCategoria = $this->createQueryBuilder('p')
            ->select('p.categoria, COUNT(p.id) as cantidad')
            ->where('p.activo = :activo')
            ->setParameter('activo', true)
            ->groupBy('p.categoria')
            ->getQuery()
            ->getResult();

        return [
            'total_productos' => $total,
            'por_categoria' => $porCategoria
        ];
    }
}
