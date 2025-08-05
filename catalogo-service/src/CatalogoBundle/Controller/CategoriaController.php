<?php

namespace CatalogoBundle\Controller;

use FOS\RestBundle\Controller\FOSRestController;
use FOS\RestBundle\Controller\Annotations as Rest;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Nelmio\ApiDocBundle\Annotation\ApiDoc;
use CatalogoBundle\DTO\CategoriaDTO;
use CatalogoBundle\Service\CategoriaService;

/**
 * @Rest\Route("/api/categorias")
 */
class CategoriaController extends FOSRestController
{
    /**
     * @Rest\Get("")
     * @Rest\View(serializerGroups={"categoria_list"})
     * @ApiDoc(description="Lista todas las categorías activas.", section="Categorías")
     */
    public function listAction()
    {
        error_log("=== CATEGORIA CONTROLLER EJECUTADO ===");
        file_put_contents('/var/www/html/var/logs/dev.log', '[' . date('Y-m-d H:i:s') . '] CATEGORIA_CONTROLLER: Controller ejecutado directamente' . "\n", FILE_APPEND);
        
        // === TEST DE ENTORNO Y LOGGING ===
        $kernel = $this->get('kernel');
        $environment = $kernel->getEnvironment();
        
        $this->get('logger')->info('=== INICIO DE PETICIÓN ===', [
            'environment' => $environment,
            'debug_mode' => $kernel->isDebug(),
            'timestamp' => date('Y-m-d H:i:s'),
            'method' => 'GET',
            'endpoint' => '/api/categorias'
        ]);
        
        $this->get('logger')->info('CategoriaController: Solicitud para listar todas las categorías.');
        
        try {
            $categorias = $this->get('catalogo.service.categoria')->obtenerTodas();
            
            $this->get('logger')->info('=== PETICIÓN EXITOSA ===', [
                'total_categorias' => count($categorias),
                'environment' => $environment
            ]);
            
            return $this->view(['success' => true, 'data' => $categorias], Response::HTTP_OK);
        } catch (\Exception $e) {
            $this->get('logger')->error('=== ERROR EN PETICIÓN ===', [
                'error_message' => $e->getMessage(),
                'error_class' => get_class($e),
                'environment' => $environment
            ]);
            throw $e;
        }
    }

    /**
     * @Rest\Get("/{id<\d+>}")
     * @Rest\View(serializerGroups={"categoria_detail"})
     * @ApiDoc(description="Obtiene los detalles de una categoría específica por su ID.", section="Categorías")
     */
    public function getAction(int $id)
    {
        $this->get('logger')->info('CategoriaController: Solicitud para obtener categoría.', ['id' => $id]);
        $categoria = $this->get('catalogo.service.categoria')->obtenerPorId($id);
        return $this->view(['success' => true, 'data' => $categoria], Response::HTTP_OK);
    }

    /**
     * @Rest\Post("")
     * @Rest\View(serializerGroups={"categoria_detail"}, statusCode=Response::HTTP_CREATED)
     * @ApiDoc(description="Crea una nueva categoría.", section="Categorías", input={"class"="CatalogoBundle\DTO\CategoriaDTO"})
     */
    public function createAction(Request $request)
    {
        $datos = json_decode($request->getContent(), true) ?: [];
        $this->get('logger')->info('CategoriaController: Solicitud para crear categoría.', ['request_data' => $datos]);
        
        $dto = new CategoriaDTO($datos);
        $categoria = $this->get('catalogo.service.categoria')->crear($dto);
        
        return $this->view(['success' => true, 'data' => $categoria], Response::HTTP_CREATED);
    }

    /**
     * @Rest\Put("/{id<\d+>}")
     * @Rest\View(serializerGroups={"categoria_detail"})
     * @ApiDoc(description="Actualiza una categoría existente.", section="Categorías", input={"class"="CatalogoBundle\DTO\CategoriaDTO"})
     */
    public function updateAction(int $id, Request $request)
    {
        $datos = json_decode($request->getContent(), true) ?: [];
        $this->get('logger')->info('CategoriaController: Solicitud para actualizar categoría.', ['id' => $id, 'request_data' => $datos]);
        
        $dto = new CategoriaDTO($datos);
        $categoria = $this->get('catalogo.service.categoria')->actualizar($id, $dto);
        
        return $this->view(['success' => true, 'data' => $categoria], Response::HTTP_OK);
    }

    /**
     * @Rest\Delete("/{id<\d+>}")
     * @Rest\View(statusCode=Response::HTTP_NO_CONTENT)
     * @ApiDoc(description="Elimina (desactiva) una categoría.", section="Categorías")
     */
    public function deleteAction(int $id)
    {
        $this->get('logger')->info('CategoriaController: Solicitud para eliminar categoría.', ['id' => $id]);
        $this->get('catalogo.service.categoria')->eliminar($id);
        return $this->view(null, Response::HTTP_NO_CONTENT);
    }
}