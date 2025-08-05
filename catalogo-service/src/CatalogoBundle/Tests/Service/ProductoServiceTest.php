<?php

namespace CatalogoBundle\Tests\Service;

use CatalogoBundle\Tests\CatalogoBundleTestCase;
use CatalogoBundle\Service\ProductoService;
use CatalogoBundle\DTO\ProductoDTO;
use CatalogoBundle\Entity\Producto;
use CatalogoBundle\Exception\ProductoNotFoundException;
use CatalogoBundle\Exception\DuplicateSkuException;
use CatalogoBundle\Exception\ValidationException;

/**
 * Test unitarios para ProductoService
 */
class ProductoServiceTest extends CatalogoBundleTestCase
{
    /**
     * @var ProductoService
     */
    private $productoService;

    /**
     * @var \Doctrine\ORM\EntityManagerInterface
     */
    private $em;

    protected function setUp(): void
    {
        parent::setUp();
        
        $this->productoService = $this->getService('catalogo.service.producto');
        $this->em = $this->getEntityManager();
    }

    protected function tearDown(): void
    {
        parent::tearDown();
    }

    /**
     * Test: Crear producto con datos válidos
     */
    public function testCrearProductoValido()
    {
        $dto = new ProductoDTO();
        $dto->setNombre('Test Producto Unitario');
        $dto->setSku('TEST_UNIT_001');
        $dto->setCategoria('secos');
        $dto->setUnidadMedida('kg');
        $dto->setPeso(1000);
        $dto->setDescripcion('Producto de prueba para test unitario');

        $producto = $this->productoService->crear($dto);

        $this->assertInstanceOf(Producto::class, $producto);
        $this->assertEquals('Test Producto Unitario', $producto->getNombre());
        $this->assertEquals('TEST_UNIT_001', $producto->getSku());
        $this->assertEquals('secos', $producto->getCategoria());
        $this->assertEquals('kg', $producto->getUnidadMedida());
        $this->assertEquals(1000, $producto->getPeso());
        $this->assertTrue($producto->getActivo());
        $this->assertNotNull($producto->getId());

        // Limpiar
        $this->em->remove($producto);
        $this->em->flush();
    }

    /**
     * Test: Crear producto con SKU duplicado debe fallar
     */
    public function testCrearProductoConSkuDuplicado()
    {
        // Crear primer producto
        $dto1 = new ProductoDTO();
        $dto1->setNombre('Primer Producto');
        $dto1->setSku('SKU_DUPLICADO_TEST');
        $dto1->setCategoria('secos');
        $dto1->setUnidadMedida('kg');
        $dto1->setPeso(500);

        $producto1 = $this->productoService->crear($dto1);

        // Intentar crear segundo producto con mismo SKU
        $dto2 = new ProductoDTO();
        $dto2->setNombre('Segundo Producto');
        $dto2->setSku('SKU_DUPLICADO_TEST');
        $dto2->setCategoria('refrigerados');
        $dto2->setUnidadMedida('litro');
        $dto2->setPeso(750);

        $this->expectException(DuplicateSkuException::class);
        
        try {
            $this->productoService->crear($dto2);
        } finally {
            // Limpiar
            $this->em->remove($producto1);
            $this->em->flush();
        }
    }

    /**
     * Test: Crear producto con categoría inválida debe fallar
     */
    public function testCrearProductoConCategoriaInvalida()
    {
        $dto = new ProductoDTO();
        $dto->setNombre('Producto Categoría Inválida');
        $dto->setSku('TEST_CAT_INVALID');
        $dto->setCategoria('categoria_inexistente');
        $dto->setUnidadMedida('kg');
        $dto->setPeso(1000);

        $this->expectException(ValidationException::class);
        $this->productoService->crear($dto);
    }

    /**
     * Test: Crear producto sin campos obligatorios debe fallar
     */
    public function testCrearProductoSinCamposObligatorios()
    {
        $dto = new ProductoDTO();
        $dto->setNombre('Producto Incompleto');
        // Falta SKU, categoría, unidad_medida, peso

        $this->expectException(ValidationException::class);
        $this->productoService->crear($dto);
    }

    /**
     * Test: Obtener producto por ID existente
     */
    public function testObtenerProductoPorIdExistente()
    {
        // Crear producto de prueba
        $dto = new ProductoDTO();
        $dto->setNombre('Producto Para Obtener');
        $dto->setSku('TEST_OBTENER_001');
        $dto->setCategoria('congelados');
        $dto->setUnidadMedida('unidad');
        $dto->setPeso(250);

        $productoCreado = $this->productoService->crear($dto);
        $id = $productoCreado->getId();

        // Obtener el producto
        $productoObtenido = $this->productoService->obtenerPorId($id);

        $this->assertEquals($id, $productoObtenido->getId());
        $this->assertEquals('Producto Para Obtener', $productoObtenido->getNombre());
        $this->assertEquals('TEST_OBTENER_001', $productoObtenido->getSku());

        // Limpiar
        $this->em->remove($productoCreado);
        $this->em->flush();
    }

    /**
     * Test: Obtener producto por ID inexistente debe fallar
     */
    public function testObtenerProductoPorIdInexistente()
    {
        $idInexistente = 999999;

        $this->expectException(ProductoNotFoundException::class);
        $this->productoService->obtenerPorId($idInexistente);
    }

    /**
     * Test: Actualizar producto existente
     */
    public function testActualizarProductoExistente()
    {
        // Crear producto de prueba
        $dto = new ProductoDTO();
        $dto->setNombre('Producto Original');
        $dto->setSku('TEST_UPDATE_001');
        $dto->setCategoria('secos');
        $dto->setUnidadMedida('kg');
        $dto->setPeso(1000);

        $producto = $this->productoService->crear($dto);
        $id = $producto->getId();

        // Actualizar producto
        $dtoUpdate = new ProductoDTO();
        $dtoUpdate->setNombre('Producto Actualizado');
        $dtoUpdate->setPeso(1500);

        $productoActualizado = $this->productoService->actualizar($id, $dtoUpdate);

        $this->assertEquals('Producto Actualizado', $productoActualizado->getNombre());
        $this->assertEquals(1500, $productoActualizado->getPeso());
        $this->assertEquals('TEST_UPDATE_001', $productoActualizado->getSku()); // No debería cambiar
        $this->assertEquals('secos', $productoActualizado->getCategoria()); // No debería cambiar

        // Limpiar
        $this->em->remove($productoActualizado);
        $this->em->flush();
    }

    /**
     * Test: Desactivar producto usando actualizar
     */
    public function testDesactivarProducto()
    {
        // Crear producto de prueba
        $dto = new ProductoDTO();
        $dto->setNombre('Producto Para Desactivar');
        $dto->setSku('TEST_DEACTIVATE_001');
        $dto->setCategoria('refrigerados');
        $dto->setUnidadMedida('litro');
        $dto->setPeso(500);

        $producto = $this->productoService->crear($dto);
        $id = $producto->getId();

        $this->assertTrue($producto->getActivo());

        // Desactivar producto
        $dtoUpdate = new ProductoDTO();
        $dtoUpdate->setActivo(false);

        $productoDesactivado = $this->productoService->actualizar($id, $dtoUpdate);

        $this->assertFalse($productoDesactivado->getActivo());

        // Limpiar
        $this->em->remove($productoDesactivado);
        $this->em->flush();
    }

    /**
     * Test: Eliminar producto permanentemente
     */
    public function testEliminarProductoPermanentemente()
    {
        // Crear producto de prueba
        $dto = new ProductoDTO();
        $dto->setNombre('Producto Para Eliminar');
        $dto->setSku('TEST_DELETE_001');
        $dto->setCategoria('secos');
        $dto->setUnidadMedida('kg');
        $dto->setPeso(800);

        $producto = $this->productoService->crear($dto);
        $id = $producto->getId();

        // Verificar que existe
        $productoAntes = $this->productoService->obtenerPorId($id);
        $this->assertNotNull($productoAntes);

        // Eliminar producto
        $resultado = $this->productoService->eliminar($id);
        $this->assertTrue($resultado);

        // Verificar que ya no existe
        $this->expectException(ProductoNotFoundException::class);
        $this->productoService->obtenerPorId($id);
    }

    /**
     * Test: Obtener todos los productos con paginación
     */
    public function testObtenerTodosConPaginacion()
    {
        // Crear varios productos de prueba
        $productos = [];
        for ($i = 1; $i <= 5; $i++) {
            $dto = new ProductoDTO();
            $dto->setNombre("Producto Paginación $i");
            $dto->setSku("TEST_PAG_00$i");
            $dto->setCategoria('secos');
            $dto->setUnidadMedida('kg');
            $dto->setPeso(100 * $i);

            $productos[] = $this->productoService->crear($dto);
        }

        // Obtener con paginación
        $resultado = $this->productoService->obtenerTodos(1, 3, []);

        $this->assertArrayHasKey('productos', $resultado);
        $this->assertArrayHasKey('total', $resultado);
        $this->assertArrayHasKey('page', $resultado);
        $this->assertArrayHasKey('limit', $resultado);
        $this->assertArrayHasKey('pages', $resultado);

        $this->assertGreaterThanOrEqual(5, $resultado['total']);
        $this->assertEquals(1, $resultado['page']);
        $this->assertEquals(3, $resultado['limit']);

        // Limpiar
        foreach ($productos as $producto) {
            $this->em->remove($producto);
        }
        $this->em->flush();
    }

    /**
     * Test: Obtener todos los productos sin paginación
     */
    public function testObtenerTodosSinPaginacion()
    {
        // Crear algunos productos de prueba
        $productos = [];
        for ($i = 1; $i <= 3; $i++) {
            $dto = new ProductoDTO();
            $dto->setNombre("Producto Sin Paginación $i");
            $dto->setSku("TEST_NOPAG_00$i");
            $dto->setCategoria('congelados');
            $dto->setUnidadMedida('unidad');
            $dto->setPeso(50 * $i);

            $productos[] = $this->productoService->crear($dto);
        }

        // Obtener sin paginación
        $resultado = $this->productoService->obtenerTodos(1, 20, [], true);

        $this->assertArrayHasKey('productos', $resultado);
        $this->assertArrayHasKey('total', $resultado);
        $this->assertArrayNotHasKey('page', $resultado);
        $this->assertArrayNotHasKey('limit', $resultado);
        $this->assertArrayNotHasKey('pages', $resultado);

        // Limpiar
        foreach ($productos as $producto) {
            $this->em->remove($producto);
        }
        $this->em->flush();
    }

    /**
     * Test: Filtrar productos por categoría
     */
    public function testFiltrarProductosPorCategoria()
    {
        // Crear productos de diferentes categorías
        $productos = [];
        
        $dto1 = new ProductoDTO();
        $dto1->setNombre('Producto Filtro Refrigerado');
        $dto1->setSku('TEST_FILT_REF_001');
        $dto1->setCategoria('refrigerados');
        $dto1->setUnidadMedida('kg');
        $dto1->setPeso(500);
        $productos[] = $this->productoService->crear($dto1);

        $dto2 = new ProductoDTO();
        $dto2->setNombre('Producto Filtro Seco');
        $dto2->setSku('TEST_FILT_SEC_001');
        $dto2->setCategoria('secos');
        $dto2->setUnidadMedida('kg');
        $dto2->setPeso(300);
        $productos[] = $this->productoService->crear($dto2);

        // Filtrar por refrigerados
        $filtros = ['categoria' => 'refrigerados'];
        $resultado = $this->productoService->obtenerTodos(1, 20, $filtros);

        $productosEncontrados = $resultado['productos'];
        $encontradoRefrigerado = false;
        $encontradoSeco = false;

        foreach ($productosEncontrados as $producto) {
            if ($producto->getSku() === 'TEST_FILT_REF_001') {
                $encontradoRefrigerado = true;
            }
            if ($producto->getSku() === 'TEST_FILT_SEC_001') {
                $encontradoSeco = true;
            }
        }

        $this->assertTrue($encontradoRefrigerado);
        $this->assertFalse($encontradoSeco);

        // Limpiar
        foreach ($productos as $producto) {
            $this->em->remove($producto);
        }
        $this->em->flush();
    }

    /**
     * Test: Búsqueda general por término
     */
    public function testBusquedaGeneralPorTermino()
    {
        // Crear producto de prueba
        $dto = new ProductoDTO();
        $dto->setNombre('Producto Búsqueda Especial');
        $dto->setSku('SEARCH_SPECIAL_001');
        $dto->setCategoria('secos');
        $dto->setUnidadMedida('kg');
        $dto->setPeso(750);
        $dto->setDescripcion('Descripción única para búsqueda');

        $producto = $this->productoService->crear($dto);

        // Buscar por término en nombre
        $filtros = ['q' => 'Búsqueda Especial'];
        $resultado = $this->productoService->obtenerTodos(1, 20, $filtros);

        $encontrado = false;
        foreach ($resultado['productos'] as $prod) {
            if ($prod->getSku() === 'SEARCH_SPECIAL_001') {
                $encontrado = true;
                break;
            }
        }

        $this->assertTrue($encontrado);

        // Limpiar
        $this->em->remove($producto);
        $this->em->flush();
    }
}
