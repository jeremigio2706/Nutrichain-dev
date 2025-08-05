<?php

namespace CatalogoBundle\Repository;

use Doctrine\ORM\EntityRepository;

class CategoriaRepository extends EntityRepository
{
    /**
     * Verifica si existe una categoría con el código dado, excluyendo un ID opcional.
     *
     * @param string $codigo
     * @param int|null $excludeId
     * @return bool
     */
    public function existeCodigo(string $codigo, ?int $excludeId = null): bool
    {
        $qb = $this->createQueryBuilder('c')
            ->select('COUNT(c.id)')
            ->where('c.codigo = :codigo')
            ->setParameter('codigo', $codigo);

        if ($excludeId !== null) {
            $qb->andWhere('c.id != :excludeId')
               ->setParameter('excludeId', $excludeId);
        }

        return $qb->getQuery()->getSingleScalarResult() > 0;
    }
}
