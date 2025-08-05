<?php

namespace CatalogoBundle\Tests\Controller;

use CatalogoBundle\Tests\CatalogoBundleTestCase;
use CatalogoBundle\DTO\ProductoDTO;
use CatalogoBundle\Entity\Producto;

/**
 * Test de integración para ProductoController
 */
class ProductoControllerTest extends CatalogoBundleTestCase
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
     * Test: GET /api/productos - Obtener todos los productos
     */
    public function testGetProductos()
    {
        $client = static::createClient();
        
        $crawler = $client->request('GET', '/api/productos', [], [], ['HTTP_ACCEPT' => 'application/json']);
        
        $this->assertEquals(200, $client->getResponse()->getStatusCode());
        
        $response = json_decode($client->getResponse()->getContent(), true);
        $this->assertNotNull($response);
        
        // Verificar la estructura de respuesta actualizada
        $this->assertArrayHasKey('success', $response);
        $this->assertArrayHasKey('data', $response);
        $this->assertArrayHasKey('total', $response);
        $this->assertTrue($response['success']);
        $this->assertTrue(is_array($response['data']));
    }

    /**
     * Test: GET /api/productos con filtros de búsqueda
     */
    public function testGetProductosConFiltros()
    {
        $client = static::createClient();
        
        // Crear producto de prueba
        $productoService = $this->getService('catalogo.service.producto');
        $dto = new ProductoDTO();
        $dto->setNombre('Producto Test Controller');
        $dto->setSku('TEST_CONTROLLER_001_' . time());
        $dto->setCategoria('secos');
        $dto->setUnidadMedida('kg');
        $dto->setPeso(1000);
        
        $producto = $productoService->crear($dto);
        
        try {
            // Test filtro por categoría
            $crawler = $client->request('GET', '/api/productos?categoria=secos', [], [], ['HTTP_ACCEPT' => 'application/json']);
            $this->assertEquals(200, $client->getResponse()->getStatusCode());
            
            $response = json_decode($client->getResponse()->getContent(), true);
            $this->assertNotNull($response);
            if (isset($response['total'])) {
                $this->assertGreaterThan(0, $response['total']);
            }
            
            // Test búsqueda por término
            $crawler = $client->request('GET', '/api/productos?q=Test Controller', [], [], ['HTTP_ACCEPT' => 'application/json']);
            $this->assertEquals(200, $client->getResponse()->getStatusCode());
            
            $response = json_decode($client->getResponse()->getContent(), true);
            $this->assertNotNull($response);
            $encontrado = false;
            if (isset($response['data']) && is_array($response['data'])) {
                foreach ($response['data'] as $prod) {
                    if (isset($prod['sku']) && strpos($prod['sku'], 'TEST_CONTROLLER_001_') === 0) {
                        $encontrado = true;
                        break;
                    }
                }
            }
            $this->assertTrue($encontrado);
            
            // Test filtro por SKU
            $crawler = $client->request('GET', '/api/productos?sku=' . $dto->getSku(), [], [], ['HTTP_ACCEPT' => 'application/json']);
            $this->assertEquals(200, $client->getResponse()->getStatusCode());
            
            $response = json_decode($client->getResponse()->getContent(), true);
            $this->assertNotNull($response);
            if (isset($response['total']) && isset($response['data'][0]['sku'])) {
                $this->assertEquals(1, $response['total']);
                $this->assertEquals($dto->getSku(), $response['data'][0]['sku']);
            }
            
        } finally {
            // Limpiar - refrescar entidad desde BD antes de eliminar
            $this->em->clear();
            $productoParaEliminar = $this->em->getRepository('CatalogoBundle:Producto')->find($producto->getId());
            if ($productoParaEliminar) {
                $this->em->remove($productoParaEliminar);
                $this->em->flush();
            }
        }
    }

    /**
     * Test: GET /api/productos con paginación
     */
    public function testGetProductosConPaginacion()
    {
        $client = static::createClient();
        
        // Test página 1 con límite 5
        $crawler = $client->request('GET', '/api/productos?page=1&limit=5', [], [], ['HTTP_ACCEPT' => 'application/json']);
        $this->assertEquals(200, $client->getResponse()->getStatusCode());
        
        $response = json_decode($client->getResponse()->getContent(), true);
        $this->assertNotNull($response);
        
        if (isset($response['pagination'])) {
            $this->assertEquals(1, $response['pagination']['page']);
            $this->assertEquals(5, $response['pagination']['limit']);
        }
        if (isset($response['data'])) {
            $this->assertLessThanOrEqual(5, count($response['data']));
        }
    }

    /**
     * Test: GET /api/productos sin paginación
     */
    public function testGetProductosSinPaginacion()
    {
        $client = static::createClient();
        
        $crawler = $client->request('GET', '/api/productos?no_pagination=true', [], [], ['HTTP_ACCEPT' => 'application/json']);
        $this->assertEquals(200, $client->getResponse()->getStatusCode());
        
        $response = json_decode($client->getResponse()->getContent(), true);
        $this->assertNotNull($response);
        
        $this->assertArrayHasKey('data', $response);
        $this->assertArrayHasKey('total', $response);
        $this->assertArrayNotHasKey('pagination', $response);
    }

    /**
     * Test: GET /api/productos/{id} - Obtener producto existente
     */
    public function testGetProductoExistente()
    {
        $client = static::createClient();
        
        // Crear producto de prueba
        $productoService = $this->getService('catalogo.service.producto');
        $dto = new ProductoDTO();
        $dto->setNombre('Producto Get Test');
        $dto->setSku('GET_TEST_001_' . time());
        $dto->setCategoria('refrigerados');
        $dto->setUnidadMedida('litro');
        $dto->setPeso(500);
        $dto->setDescripcion('Descripción para test GET');
        
        $producto = $productoService->crear($dto);
        $id = $producto->getId();
        
        try {
            $crawler = $client->request('GET', "/api/productos/$id", [], [], ['HTTP_ACCEPT' => 'application/json']);
            $this->assertEquals(200, $client->getResponse()->getStatusCode());
            
            $responseContent = $client->getResponse()->getContent();
            $response = json_decode($responseContent, true);
            $this->assertNotNull($response, 'Response should not be null. Content: ' . $responseContent);
            
            if (isset($response['success']) && $response['success'] && isset($response['data'])) {
                $this->assertEquals($id, $response['data']['id']);
                $this->assertEquals('Producto Get Test', $response['data']['nombre']);
                $this->assertStringStartsWith('GET_TEST_001_', $response['data']['sku']);
                $this->assertEquals('refrigerados', $response['data']['categoria']);
                $this->assertEquals('litro', $response['data']['unidad_medida']);
                $this->assertEquals(500, $response['data']['peso']);
            }
            
        } finally {
            // Limpiar - refrescar entidad desde BD antes de eliminar
            $this->em->clear();
            $productoParaEliminar = $this->em->getRepository('CatalogoBundle:Producto')->find($producto->getId());
            if ($productoParaEliminar) {
                $this->em->remove($productoParaEliminar);
                $this->em->flush();
            }
        }
    }

    /**
     * Test: GET /api/productos/{id} - Producto inexistente
     */
    public function testGetProductoInexistente()
    {
        $client = static::createClient();
        
        $idInexistente = 999999;
        $crawler = $client->request('GET', "/api/productos/$idInexistente", [], [], ['HTTP_ACCEPT' => 'application/json']);
        
        $this->assertEquals(404, $client->getResponse()->getStatusCode());
        $responseContent = $client->getResponse()->getContent();
        $response = json_decode($responseContent, true);
        $this->assertNotNull($response, 'Response should not be null. Content: ' . $responseContent);
        
        if (isset($response['success'])) {
            $this->assertFalse($response['success']);
            if (isset($response['error'])) {
                $this->assertContains('no encontrado', strtolower($response['error']));
            }
        }
    }

    /**
     * Test: POST /api/productos - Crear producto válido
     */
    public function testPostProductoValido()
    {
        $client = static::createClient();
        
        $data = [
            'nombre' => 'Producto Post Test',
            'sku' => 'POST_TEST_001_' . time(),
            'categoria' => 'congelados',
            'unidad_medida' => 'unidad',
            'peso' => 250,
            'descripcion' => 'Descripción para test POST'
        ];
        
        $crawler = $client->request(
            'POST',
            '/api/productos',
            [],
            [],
            ['CONTENT_TYPE' => 'application/json', 'HTTP_ACCEPT' => 'application/json'],
            json_encode($data)
        );
        
        $this->assertEquals(201, $client->getResponse()->getStatusCode());
        
        $responseContent = $client->getResponse()->getContent();
        $response = json_decode($responseContent, true);
        $this->assertNotNull($response, 'Response should not be null. Content: ' . $responseContent);
        
        if (isset($response['success']) && $response['success'] && isset($response['data'])) {
            $this->assertEquals('Producto Post Test', $response['data']['nombre']);
            $this->assertStringStartsWith('POST_TEST_001_', $response['data']['sku']);
            $this->assertEquals('congelados', $response['data']['categoria']);
            $this->assertTrue($response['data']['activo']);
            
            // Limpiar
            $producto = $this->em->getRepository('CatalogoBundle:Producto')->find($response['data']['id']);
            if ($producto) {
                $this->em->remove($producto);
                $this->em->flush();
            }
        }
    }

    /**
     * Test: POST /api/productos - Crear producto con datos inválidos
     */
    public function testPostProductoInvalido()
    {
        $client = static::createClient();
        
        // Datos incompletos (falta SKU)
        $data = [
            'nombre' => 'Producto Inválido',
            'categoria' => 'secos',
            'unidad_medida' => 'kg'
            // Falta sku y peso
        ];
        
        $crawler = $client->request(
            'POST',
            '/api/productos',
            [],
            [],
            ['CONTENT_TYPE' => 'application/json', 'HTTP_ACCEPT' => 'application/json'],
            json_encode($data)
        );
        
        $this->assertEquals(400, $client->getResponse()->getStatusCode());
        $responseContent = $client->getResponse()->getContent();
        $response = json_decode($responseContent, true);
        $this->assertNotNull($response, 'Response should not be null. Content: ' . $responseContent);
        
        if (isset($response['success'])) {
            $this->assertFalse($response['success']);
            $this->assertTrue(isset($response['error']) || isset($response['message']));
        }
    }

    /**
     * Test: POST /api/productos - SKU duplicado
     */
    public function testPostProductoSkuDuplicado()
    {
        $client = static::createClient();
        
        // Crear primer producto
        $productoService = $this->getService('catalogo.service.producto');
        $dto = new ProductoDTO();
        $dto->setNombre('Producto Original');
        $dto->setSku('SKU_DUPLICADO_CONTROLLER_' . time());
        $dto->setCategoria('secos');
        $dto->setUnidadMedida('kg');
        $dto->setPeso(1000);
        
        $producto = $productoService->crear($dto);
        
        try {
            // Intentar crear segundo producto con mismo SKU
            $data = [
                'nombre' => 'Producto Duplicado',
                'sku' => $dto->getSku(),
                'categoria' => 'refrigerados',
                'unidad_medida' => 'litro',
                'peso' => 500
            ];
            
            $crawler = $client->request(
                'POST',
                '/api/productos',
                [],
                [],
                ['CONTENT_TYPE' => 'application/json', 'HTTP_ACCEPT' => 'application/json'],
                json_encode($data)
            );
            
            $this->assertEquals(409, $client->getResponse()->getStatusCode());
            $responseContent = $client->getResponse()->getContent();
            $response = json_decode($responseContent, true);
            $this->assertNotNull($response, 'Response should not be null. Content: ' . $responseContent);
            
            if (isset($response['success'])) {
                $this->assertFalse($response['success']);
                if (isset($response['error'])) {
                    $this->assertContains('sku', strtolower($response['error']));
                }
            }
            
        } finally {
            // Limpiar - refrescar entidad desde BD antes de eliminar
            $this->em->clear();
            $productoParaEliminar = $this->em->getRepository('CatalogoBundle:Producto')->find($producto->getId());
            if ($productoParaEliminar) {
                $this->em->remove($productoParaEliminar);
                $this->em->flush();
            }
        }
    }

    /**
     * Test: PUT /api/productos/{id} - Actualizar producto existente
     */
    public function testPutProductoExistente()
    {
        $client = static::createClient();
        
        // Crear producto de prueba
        $productoService = $this->getService('catalogo.service.producto');
        $dto = new ProductoDTO();
        $dto->setNombre('Producto Original Put');
        $dto->setSku('PUT_TEST_001_' . time());
        $dto->setCategoria('secos');
        $dto->setUnidadMedida('kg');
        $dto->setPeso(1000);
        
        $producto = $productoService->crear($dto);
        $id = $producto->getId();
        
        try {
            // Datos para actualizar
            $data = [
                'nombre' => 'Producto Actualizado Put',
                'peso' => 1500,
                'descripcion' => 'Nueva descripción'
            ];
            
            $crawler = $client->request(
                'PUT',
                "/api/productos/$id",
                [],
                [],
                ['CONTENT_TYPE' => 'application/json', 'HTTP_ACCEPT' => 'application/json'],
                json_encode($data)
            );
            
            $this->assertEquals(200, $client->getResponse()->getStatusCode());
            $responseContent = $client->getResponse()->getContent();
            $response = json_decode($responseContent, true);
            $this->assertNotNull($response, 'Response should not be null. Content: ' . $responseContent);
            
            if (isset($response['success']) && $response['success'] && isset($response['data'])) {
                $this->assertEquals('Producto Actualizado Put', $response['data']['nombre']);
                $this->assertEquals(1500, $response['data']['peso']);
                $this->assertEquals('Nueva descripción', $response['data']['descripcion']);
                $this->assertStringStartsWith('PUT_TEST_001_', $response['data']['sku']); // No debería cambiar
            }
            
        } finally {
            // Limpiar - refrescar entidad desde BD antes de eliminar
            $this->em->clear();
            $productoParaEliminar = $this->em->getRepository('CatalogoBundle:Producto')->find($id);
            if ($productoParaEliminar) {
                $this->em->remove($productoParaEliminar);
                $this->em->flush();
            }
        }
    }

    /**
     * Test: PUT /api/productos/{id} - Actualizar producto inexistente
     */
    public function testPutProductoInexistente()
    {
        $client = static::createClient();
        
        $idInexistente = 999999;
        $data = [
            'nombre' => 'Producto Inexistente',
            'peso' => 500
        ];
        
        $crawler = $client->request(
            'PUT',
            "/api/productos/$idInexistente",
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
            $this->assertTrue(isset($response['error']) || isset($response['message']));
        }
    }

    /**
     * Test: DELETE /api/productos/{id} - Eliminar producto existente
     */
    public function testDeleteProductoExistente()
    {
        $client = static::createClient();
        
        // Crear producto de prueba
        $productoService = $this->getService('catalogo.service.producto');
        $dto = new ProductoDTO();
        $dto->setNombre('Producto Para Eliminar');
        $dto->setSku('DELETE_TEST_001_' . time());
        $dto->setCategoria('secos');
        $dto->setUnidadMedida('kg');
        $dto->setPeso(800);
        
        $producto = $productoService->crear($dto);
        $id = $producto->getId();
        
        // Eliminar producto
        $crawler = $client->request('DELETE', "/api/productos/$id", [], [], ['HTTP_ACCEPT' => 'application/json']);
        
        $this->assertEquals(200, $client->getResponse()->getStatusCode());
        $responseContent = $client->getResponse()->getContent();
        $response = json_decode($responseContent, true);
        $this->assertNotNull($response, 'Response should not be null. Content: ' . $responseContent);
        
        if (isset($response['success'])) {
            $this->assertTrue($response['success']);
        }
        
        // Verificar que ya no existe
        $crawler = $client->request('GET', "/api/productos/$id", [], [], ['HTTP_ACCEPT' => 'application/json']);
        $this->assertEquals(404, $client->getResponse()->getStatusCode());
    }

    /**
     * Test: DELETE /api/productos/{id} - Eliminar producto inexistente
     */
    public function testDeleteProductoInexistente()
    {
        $client = static::createClient();
        
        $idInexistente = 999999;
        $crawler = $client->request('DELETE', "/api/productos/$idInexistente", [], [], ['HTTP_ACCEPT' => 'application/json']);
        
        $this->assertEquals(404, $client->getResponse()->getStatusCode());
        $responseContent = $client->getResponse()->getContent();
        $response = json_decode($responseContent, true);
        $this->assertNotNull($response, 'Response should not be null. Content: ' . $responseContent);
        
        if (isset($response['success'])) {
            $this->assertFalse($response['success']);
            $this->assertTrue(isset($response['error']) || isset($response['message']));
        }
    }

    /**
     * Test: Métodos HTTP no permitidos
     */
    public function testMetodosNoPermitidos()
    {
        $client = static::createClient();
        
        // PATCH no permitido en colección
        $crawler = $client->request('PATCH', '/api/productos', [], [], ['HTTP_ACCEPT' => 'application/json']);
        $this->assertEquals(405, $client->getResponse()->getStatusCode());
        
        // PATCH no permitido en elemento individual
        $crawler = $client->request('PATCH', '/api/productos/1', [], [], ['HTTP_ACCEPT' => 'application/json']);
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
            'sku' => 'TEST_CT_001_' . time()
        ];
        
        // Enviar con Content-Type incorrecto
        $crawler = $client->request(
            'POST',
            '/api/productos',
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
        
        $jsonInvalido = '{"nombre": "Test", "sku": "TEST", invalid}';
        
        $crawler = $client->request(
            'POST',
            '/api/productos',
            [],
            [],
            ['CONTENT_TYPE' => 'application/json', 'HTTP_ACCEPT' => 'application/json'],
            $jsonInvalido
        );
        
        $this->assertEquals(400, $client->getResponse()->getStatusCode());
        $responseContent = $client->getResponse()->getContent();
        $response = json_decode($responseContent, true);
        $this->assertNotNull($response, 'Response should not be null. Content: ' . $responseContent);
        
        if (isset($response['success'])) {
            $this->assertFalse($response['success']);
            $this->assertTrue(isset($response['error']) || isset($response['message']));
        }
    }
}
