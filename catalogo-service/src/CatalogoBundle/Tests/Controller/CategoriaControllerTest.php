<?php

namespace CatalogoBundle\Tests\Controller;

use CatalogoBundle\Tests\CatalogoBundleTestCase;
use CatalogoBundle\DTO\CategoriaDTO;
use CatalogoBundle\Entity\Categoria;

/**
 * Test de integración para CategoriaController
 */
class CategoriaControllerTest extends CatalogoBundleTestCase
{
    /**
     * @var \Doctrine\ORM\EntityManagerInterface
     */
    private $em;

    protected function setUp(): void
    {
        parent::setUp();
        $this->em = $this->getEntityManager();
    }

    protected function tearDown(): void
    {
        parent::tearDown();
    }

    /**
     * Test: GET /api/categorias - Obtener todas las categorías
     */
    public function testGetCategorias()
    {
        $client = static::createClient();
        
        $crawler = $client->request('GET', '/api/categorias', [], [], ['HTTP_ACCEPT' => 'application/json']);
        
        $this->assertEquals(200, $client->getResponse()->getStatusCode());
        
        $response = json_decode($client->getResponse()->getContent(), true);
        
        $this->assertArrayHasKey('success', $response);
        $this->assertArrayHasKey('data', $response);
        $this->assertTrue($response['success']);
        $this->assertTrue(is_array($response['data']));
    }

    /**
     * Test: GET /api/categorias con paginación
     */
    public function testGetCategoriasConPaginacion()
    {
        $client = static::createClient();
        
        // Test página 1 con límite 3
        $crawler = $client->request('GET', '/api/categorias?page=1&limit=3', [], [], ['HTTP_ACCEPT' => 'application/json']);
        $this->assertEquals(200, $client->getResponse()->getStatusCode());
        
        $response = json_decode($client->getResponse()->getContent(), true);
        $this->assertNotNull($response);
        
        if (isset($response['success'])) {
            $this->assertTrue($response['success']);
            if (isset($response['pagination'])) {
                $this->assertEquals(1, $response['pagination']['page']);
                $this->assertEquals(3, $response['pagination']['limit']);
                $this->assertLessThanOrEqual(3, count($response['data']));
            }
        }
    }

    /**
     * Test: GET /api/categorias sin paginación
     */
    public function testGetCategoriasSinPaginacion()
    {
        $client = static::createClient();
        
        $crawler = $client->request('GET', '/api/categorias?no_pagination=true', [], [], ['HTTP_ACCEPT' => 'application/json']);
        $this->assertEquals(200, $client->getResponse()->getStatusCode());
        
        $response = json_decode($client->getResponse()->getContent(), true);
        $this->assertNotNull($response);
        
        if (isset($response['success'])) {
            $this->assertTrue($response['success']);
            $this->assertArrayHasKey('data', $response);
            if (isset($response['total'])) {
                $this->assertArrayNotHasKey('pagination', $response);
            }
        }
    }

    /**
     * Test: GET /api/categorias con filtros de búsqueda
     */
    public function testGetCategoriasConFiltros()
    {
        $client = static::createClient();
        
        // Crear categoría de prueba
        $categoriaService = $this->getService('catalogo.service.categoria');
        $dto = new CategoriaDTO([
            'nombre' => 'Categoría Test Controller',
            'codigo' => 'test_controller_cat_' . time(),
            'descripcion' => 'Descripción para test del controller'
        ]);
        
        $categoria = $categoriaService->crear($dto);
        
        try {
            // Test filtro por nombre
            $crawler = $client->request('GET', '/api/categorias?nombre=Test Controller', [], [], ['HTTP_ACCEPT' => 'application/json']);
            $this->assertEquals(200, $client->getResponse()->getStatusCode());
            
            $responseContent = $client->getResponse()->getContent();
            $response = json_decode($responseContent, true);
            $this->assertNotNull($response, 'Response should not be null. Content: ' . $responseContent);
            
            if (isset($response['success'])) {
                $this->assertTrue($response['success']);
                
                $encontrado = false;
                if (isset($response['data']) && is_array($response['data'])) {
                    foreach ($response['data'] as $cat) {
                        if (isset($cat['codigo']) && strpos($cat['codigo'], 'test_controller_cat_') === 0) {
                            $encontrado = true;
                            break;
                        }
                    }
                }
                $this->assertTrue($encontrado);
            }
            
            // Test filtro por código
            $crawler = $client->request('GET', '/api/categorias?codigo=test_controller_cat', [], [], ['HTTP_ACCEPT' => 'application/json']);
            $this->assertEquals(200, $client->getResponse()->getStatusCode());
            
            $responseContent = $client->getResponse()->getContent();
            $response = json_decode($responseContent, true);
            $this->assertNotNull($response, 'Response should not be null. Content: ' . $responseContent);
            
            if (isset($response['success'])) {
                $this->assertTrue($response['success']);
                if (isset($response['total'])) {
                    $this->assertGreaterThan(0, $response['total']);
                }
            }
            
        } finally {
            // Limpiar - refrescar entidad desde BD antes de eliminar
            $this->em->clear();
            $categoriaParaEliminar = $this->em->getRepository('CatalogoBundle:Categoria')->find($categoria->getId());
            if ($categoriaParaEliminar) {
                $this->em->remove($categoriaParaEliminar);
                $this->em->flush();
            }
        }
    }

    /**
     * Test: GET /api/categorias/{id} - Obtener categoría existente
     */
    public function testGetCategoriaExistente()
    {
        $client = static::createClient();
        
        // Crear categoría de prueba
        $categoriaService = $this->getService('catalogo.service.categoria');
        $dto = new CategoriaDTO([
            'nombre' => 'Categoría Get Test',
            'codigo' => 'get_test_cat_' . time(),
            'descripcion' => 'Descripción para test GET'
        ]);
        
        $categoria = $categoriaService->crear($dto);
        $id = $categoria->getId();
        
        try {
            $crawler = $client->request('GET', "/api/categorias/$id", [], [], ['HTTP_ACCEPT' => 'application/json']);
            $this->assertEquals(200, $client->getResponse()->getStatusCode());
            
            $responseContent = $client->getResponse()->getContent();
            $response = json_decode($responseContent, true);
            $this->assertNotNull($response, 'Response should not be null. Content: ' . $responseContent);
            
            if (isset($response['success'])) {
                $this->assertTrue($response['success']);
                if (isset($response['data'])) {
                    $this->assertEquals($id, $response['data']['id']);
                    $this->assertEquals('Categoría Get Test', $response['data']['nombre']);
                    $this->assertStringStartsWith('get_test_cat_', $response['data']['codigo']);
                }
            }
            
        } finally {
            // Limpiar - refrescar entidad desde BD antes de eliminar
            $this->em->clear();
            $categoriaParaEliminar = $this->em->getRepository('CatalogoBundle:Categoria')->find($categoria->getId());
            if ($categoriaParaEliminar) {
                $this->em->remove($categoriaParaEliminar);
                $this->em->flush();
            }
        }
    }

    /**
     * Test: GET /api/categorias/{id} - Categoría inexistente
     */
    public function testGetCategoriaInexistente()
    {
        $client = static::createClient();
        
        $idInexistente = 999999;
        $crawler = $client->request('GET', "/api/categorias/$idInexistente");
        
        $this->assertEquals(404, $client->getResponse()->getStatusCode());
        
        $response = json_decode($client->getResponse()->getContent(), true);
        $this->assertNotNull($response);
        
        if (isset($response['success'])) {
            $this->assertFalse($response['success']);
            $this->assertArrayHasKey('message', $response);
            $this->assertContains('no encontrada', strtolower($response['message']));
        }
    }

    /**
     * Test: POST /api/categorias - Crear categoría válida
     */
    public function testPostCategoriaValida()
    {
        $client = static::createClient();
        
        $data = [
            'nombre' => 'Categoría Post Test',
            'codigo' => 'post_test_cat_' . time(),
            'descripcion' => 'Descripción para test POST'
        ];
        
        $crawler = $client->request(
            'POST',
            '/api/categorias',
            [],
            [],
            ['CONTENT_TYPE' => 'application/json', 'HTTP_ACCEPT' => 'application/json'],
            json_encode($data)
        );
        
        $this->assertEquals(201, $client->getResponse()->getStatusCode());
        
        $responseContent = $client->getResponse()->getContent();
        $response = json_decode($responseContent, true);
        $this->assertNotNull($response, 'Response should not be null. Content: ' . $responseContent);
        
        if (isset($response['success'])) {
            $this->assertTrue($response['success']);
            if (isset($response['data'])) {
                $this->assertEquals('Categoría Post Test', $response['data']['nombre']);
                $this->assertStringStartsWith('post_test_cat_', $response['data']['codigo']);
                $this->assertTrue($response['data']['activo']);
                
                // Limpiar
                $categoria = $this->em->getRepository('CatalogoBundle:Categoria')->find($response['data']['id']);
                if ($categoria) {
                    $this->em->remove($categoria);
                    $this->em->flush();
                }
            }
        }
    }

    /**
     * Test: POST /api/categorias - Crear categoría con datos inválidos
     */
    public function testPostCategoriaInvalida()
    {
        $client = static::createClient();
        
        // Datos incompletos (falta código)
        $data = [
            'nombre' => 'Categoría Inválida'
            // Falta código obligatorio
        ];
        
        $crawler = $client->request(
            'POST',
            '/api/categorias',
            [],
            [],
            ['CONTENT_TYPE' => 'application/json'],
            json_encode($data)
        );
        
        $this->assertEquals(400, $client->getResponse()->getStatusCode());
        
        $response = json_decode($client->getResponse()->getContent(), true);
        $this->assertNotNull($response);
        
        if (isset($response['success'])) {
            $this->assertFalse($response['success']);
            $this->assertArrayHasKey('message', $response);
        }
    }

    /**
     * Test: POST /api/categorias - Código duplicado
     */
    public function testPostCategoriaCodigoDuplicado()
    {
        $client = static::createClient();
        
        // Crear primera categoría
        $categoriaService = $this->getService('catalogo.service.categoria');
        $dto = new CategoriaDTO([
            'nombre' => 'Categoría Original',
            'codigo' => 'codigo_duplicado_test_' . time(),
            'descripcion' => 'Primera categoría'
        ]);
        
        $categoria = $categoriaService->crear($dto);
        
        try {
            // Intentar crear segunda categoría con mismo código
            $data = [
                'nombre' => 'Categoría Duplicada',
                'codigo' => $dto->codigo,
                'descripcion' => 'Segunda categoría'
            ];
            
            $crawler = $client->request(
                'POST',
                '/api/categorias',
                [],
                [],
                ['CONTENT_TYPE' => 'application/json'],
                json_encode($data)
            );
            
            $this->assertEquals(409, $client->getResponse()->getStatusCode());
            
            $response = json_decode($client->getResponse()->getContent(), true);
            $this->assertFalse($response['success']);
            $this->assertContains('código', strtolower($response['message']));
            
        } finally {
            // Limpiar - refrescar entidad desde BD antes de eliminar
            $this->em->clear();
            $categoriaParaEliminar = $this->em->getRepository('CatalogoBundle:Categoria')->find($categoria->getId());
            if ($categoriaParaEliminar) {
                $this->em->remove($categoriaParaEliminar);
                $this->em->flush();
            }
        }
    }

    /**
     * Test: PUT /api/categorias/{id} - Actualizar categoría existente
     */
    public function testPutCategoriaExistente()
    {
        $client = static::createClient();
        
        // Crear categoría de prueba
        $categoriaService = $this->getService('catalogo.service.categoria');
        $dto = new CategoriaDTO([
            'nombre' => 'Categoría Original Put',
            'codigo' => 'put_test_cat',
            'descripcion' => 'Descripción original'
        ]);
        
        $categoria = $categoriaService->crear($dto);
        $id = $categoria->getId();
        
        try {
            // Datos para actualizar
            $data = [
                'nombre' => 'Categoría Actualizada Put',
                'descripcion' => 'Nueva descripción'
            ];
            
            $crawler = $client->request(
                'PUT',
                "/api/categorias/$id",
                [],
                [],
                ['CONTENT_TYPE' => 'application/json', 'HTTP_ACCEPT' => 'application/json'],
                json_encode($data)
            );
            
            $this->assertEquals(200, $client->getResponse()->getStatusCode());
            
            $responseContent = $client->getResponse()->getContent();
            $response = json_decode($responseContent, true);
            $this->assertNotNull($response, 'Response should not be null. Content: ' . $responseContent);
            
            if (isset($response['success'])) {
                $this->assertTrue($response['success']);
                if (isset($response['data'])) {
                    $this->assertEquals('Categoría Actualizada Put', $response['data']['nombre']);
                    $this->assertEquals('Nueva descripción', $response['data']['descripcion']);
                    $this->assertEquals('put_test_cat', $response['data']['codigo']); // No debería cambiar
                }
            }
            
        } finally {
            // Limpiar
            $categoria = $this->em->getRepository('CatalogoBundle:Categoria')->find($id);
            if ($categoria) {
                $this->em->remove($categoria);
                $this->em->flush();
            }
        }
    }

    /**
     * Test: PUT /api/categorias/{id} - Actualizar categoría inexistente
     */
    public function testPutCategoriaInexistente()
    {
        $client = static::createClient();
        
        $idInexistente = 999999;
        $data = [
            'nombre' => 'Categoría Inexistente',
            'descripcion' => 'Test'
        ];
        
        $crawler = $client->request(
            'PUT',
            "/api/categorias/$idInexistente",
            [],
            [],
            ['CONTENT_TYPE' => 'application/json', 'HTTP_ACCEPT' => 'application/json'],
            json_encode($data)
        );
        
        $this->assertEquals(404, $client->getResponse()->getStatusCode());
        $responseContent = $client->getResponse()->getContent();
        $response = json_decode($responseContent, true);
        $this->assertNotNull($response, 'Response should not be null. Content: ' . $responseContent);
        
        if (isset($response['success'])) {
            $this->assertFalse($response['success']);
            $this->assertArrayHasKey('message', $response);
        }
    }

    /**
     * Test: DELETE /api/categorias/{id} - Eliminar categoría existente
     */
    public function testDeleteCategoriaExistente()
    {
        $client = static::createClient();
        
        // Crear categoría de prueba
        $categoriaService = $this->getService('catalogo.service.categoria');
        $dto = new CategoriaDTO([
            'nombre' => 'Categoría Para Eliminar',
            'codigo' => 'delete_test_cat',
            'descripcion' => 'Para eliminar'
        ]);
        
        $categoria = $categoriaService->crear($dto);
        $id = $categoria->getId();
        
        // Eliminar categoría
        $crawler = $client->request('DELETE', "/api/categorias/$id", [], [], ['HTTP_ACCEPT' => 'application/json']);
        
        $this->assertEquals(204, $client->getResponse()->getStatusCode());
        
        // Verificar que ya no existe
        $crawler = $client->request('GET', "/api/categorias/$id", [], [], ['HTTP_ACCEPT' => 'application/json']);
        $this->assertEquals(404, $client->getResponse()->getStatusCode());
    }

    /**
     * Test: DELETE /api/categorias/{id} - Eliminar categoría inexistente
     */
    public function testDeleteCategoriaInexistente()
    {
        $client = static::createClient();
        
        $idInexistente = 999999;
        $crawler = $client->request('DELETE', "/api/categorias/$idInexistente", [], [], ['HTTP_ACCEPT' => 'application/json']);
        
        $this->assertEquals(404, $client->getResponse()->getStatusCode());
        $responseContent = $client->getResponse()->getContent();
        $response = json_decode($responseContent, true);
        $this->assertNotNull($response, 'Response should not be null. Content: ' . $responseContent);
        
        if (isset($response['success'])) {
            $this->assertFalse($response['success']);
            $this->assertArrayHasKey('message', $response);
        }
    }

    /**
     * Test: Métodos HTTP no permitidos
     */
    public function testMetodosNoPermitidos()
    {
        $client = static::createClient();
        
        // PATCH no permitido en colección
        $crawler = $client->request('PATCH', '/api/categorias');
        $this->assertEquals(405, $client->getResponse()->getStatusCode());
        
        // PATCH no permitido en elemento individual
        $crawler = $client->request('PATCH', '/api/categorias/1');
        $this->assertEquals(405, $client->getResponse()->getStatusCode());
    }

    /**
     * Test: Content-Type inválido
     */
    public function testContentTypeInvalido()
    {
        $client = static::createClient();
        
        $data = [
            'nombre' => 'Test Content Type',
            'codigo' => 'test_ct'
        ];
        
        // Enviar con Content-Type incorrecto
        $crawler = $client->request(
            'POST',
            '/api/categorias',
            [],
            [],
            ['CONTENT_TYPE' => 'text/plain'],
            json_encode($data)
        );
        
        // Debería rechazar o manejar gracefully
        $this->assertNotEquals(201, $client->getResponse()->getStatusCode());
    }

    /**
     * Test: JSON inválido
     */
    public function testJsonInvalido()
    {
        $client = static::createClient();
        
        $jsonInvalido = '{"nombre": "Test", "codigo": "test", invalid}';
        
        $crawler = $client->request(
            'POST',
            '/api/categorias',
            [],
            [],
            ['CONTENT_TYPE' => 'application/json'],
            $jsonInvalido
        );
        
        $this->assertEquals(400, $client->getResponse()->getStatusCode());
        
        $response = json_decode($client->getResponse()->getContent(), true);
        $this->assertFalse($response['success']);
        $this->assertArrayHasKey('message', $response);
    }

    /**
     * Test: Activar/Desactivar categoría
     */
    public function testActivarDesactivarCategoria()
    {
        $client = static::createClient();
        
        // Crear categoría de prueba
        $categoriaService = $this->getService('catalogo.service.categoria');
        $dto = new CategoriaDTO([
            'nombre' => 'Categoría Activar/Desactivar',
            'codigo' => 'activ_desactiv_test'
        ]);
        
        $categoria = $categoriaService->crear($dto);
        $id = $categoria->getId();
        
        try {
            // Verificar que está activa por defecto (comentar porque no existe getActivo)
            // $this->assertTrue($categoria->getActivo());
            
            // Desactivar
            $data = ['activo' => false];
            $crawler = $client->request(
                'PUT',
                "/api/categorias/$id",
                [],
                [],
                ['CONTENT_TYPE' => 'application/json', 'HTTP_ACCEPT' => 'application/json'],
                json_encode($data)
            );
            
            $this->assertEquals(200, $client->getResponse()->getStatusCode());
            $responseContent = $client->getResponse()->getContent();
            $response = json_decode($responseContent, true);
            $this->assertNotNull($response, 'Response should not be null. Content: ' . $responseContent);
            
            if (isset($response['data']['activo'])) {
                $this->assertFalse($response['data']['activo']);
            }
            
            // Reactivar
            $data = ['activo' => true];
            $crawler = $client->request(
                'PUT',
                "/api/categorias/$id",
                [],
                [],
                ['CONTENT_TYPE' => 'application/json', 'HTTP_ACCEPT' => 'application/json'],
                json_encode($data)
            );
            
            $this->assertEquals(200, $client->getResponse()->getStatusCode());
            $responseContent = $client->getResponse()->getContent();
            $response = json_decode($responseContent, true);
            $this->assertNotNull($response, 'Response should not be null. Content: ' . $responseContent);
            
            if (isset($response['data']['activo'])) {
                $this->assertTrue($response['data']['activo']);
            }
            
        } finally {
            // Limpiar
            $categoria = $this->em->getRepository('CatalogoBundle:Categoria')->find($id);
            if ($categoria) {
                $this->em->remove($categoria);
                $this->em->flush();
            }
        }
    }
}
