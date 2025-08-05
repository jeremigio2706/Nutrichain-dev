<?php

namespace CatalogoBundle\Controller;

use FOS\RestBundle\Controller\FOSRestController;
use FOS\RestBundle\Controller\Annotations as Rest;
use Symfony\Component\HttpFoundation\Response;
use Nelmio\ApiDocBundle\Annotation\ApiDoc;

/**
 * Controlador para endpoints generales de la API
 */
class ApiController extends FOSRestController
{
    /**
     * Estado y información del servicio de catálogo
     *
     * @ApiDoc(
     *     description="Obtiene información sobre el estado del servicio de catálogo",
     *     section="General",
     *     statusCodes={
     *         200="Servicio funcionando correctamente",
     *         500="Error en el servicio"
     *     }
     * )
     * @Rest\Get("/status")
     */
    public function statusAction()
    {
        try {
            // Verificar conexión a base de datos
            $em = $this->getDoctrine()->getManager();
            $connection = $em->getConnection();
            $connection->connect();

            // Obtener estadísticas básicas
            $categoriaRepo = $em->getRepository('CatalogoBundle:Categoria');
            $productoRepo = $em->getRepository('CatalogoBundle:Producto');

            $totalCategorias = $categoriaRepo->createQueryBuilder('c')
                ->select('COUNT(c.id)')
                ->where('c.activo = :activo')
                ->setParameter('activo', true)
                ->getQuery()
                ->getSingleScalarResult();

            $totalProductos = $productoRepo->createQueryBuilder('p')
                ->select('COUNT(p.id)')
                ->where('p.activo = :activo')
                ->setParameter('activo', true)
                ->getQuery()
                ->getSingleScalarResult();

            return $this->view([
                'success' => true,
                'service' => 'Catálogo NutriChain',
                'version' => '1.0.0',
                'status' => 'active',
                'timestamp' => date('Y-m-d H:i:s'),
                'database' => [
                    'connected' => true,
                    'driver' => $connection->getDriver()->getName()
                ],
                'statistics' => [
                    'categorias_activas' => (int)$totalCategorias,
                    'productos_activos' => (int)$totalProductos
                ],
                'endpoints' => [
                    'categorias' => '/api/categorias',
                    'productos' => '/api/productos',
                    'documentacion' => '/api/doc'
                ]
            ], Response::HTTP_OK);

        } catch (\Exception $e) {
            return $this->view([
                'success' => false,
                'service' => 'Catálogo NutriChain',
                'status' => 'error',
                'timestamp' => date('Y-m-d H:i:s'),
                'error' => $e->getMessage(),
                'database' => [
                    'connected' => false
                ]
            ], Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }
}
