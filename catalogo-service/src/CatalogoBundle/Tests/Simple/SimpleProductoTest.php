<?php

namespace CatalogoBundle\Tests\Simple;

use CatalogoBundle\Service\ProductoService;
use CatalogoBundle\DTO\ProductoDTO;

/**
 * Test simple para verificar funcionalidad básica
 */
class SimpleProductoTest
{
    private $container;
    private $kernel;

    public function __construct()
    {
        // Configurar kernel de Symfony manualmente
        require_once '/var/www/html/app/bootstrap.php.cache';
        require_once '/var/www/html/app/AppKernel.php';
        
        $this->kernel = new \AppKernel('test', false);
        $this->kernel->boot();
        $this->container = $this->kernel->getContainer();
    }

    public function setUp()
    {
        // Configurar base de datos de test
        $em = $this->container->get('doctrine.orm.entity_manager');
        
        try {
            // Limpiar datos existentes de manera más simple
            $connection = $em->getConnection();
            $connection->exec('DELETE FROM productos');
            $connection->exec('DELETE FROM categorias');
            // Reiniciar secuencias
            $connection->exec('ALTER SEQUENCE productos_id_seq RESTART WITH 1');
            $connection->exec('ALTER SEQUENCE categorias_id_seq RESTART WITH 1');
        } catch (\Exception $e) {
            // Si hay error, intentar crear el esquema
            $schemaTool = new \Doctrine\ORM\Tools\SchemaTool($em);
            $metadata = $em->getMetadataFactory()->getAllMetadata();
            try {
                $schemaTool->createSchema($metadata);
            } catch (\Exception $e2) {
                echo "⚠️  Advertencia: No se pudo preparar la BD de test: " . $e2->getMessage() . "\n";
            }
        }
    }

    public function testCrearProducto()
    {
        echo "🧪 Test: Crear producto...\n";
        
        $productoService = $this->container->get('catalogo.service.producto');
        
        $dto = new ProductoDTO();
        $dto->setNombre('Producto Test Simple');
        $dto->setSku('TEST_SIMPLE_001');
        $dto->setCategoria('secos');
        $dto->setUnidadMedida('kg');
        $dto->setPeso(1000);
        $dto->setDescripcion('Test simple de creación');
        
        $producto = $productoService->crear($dto);
        
        $this->assert($producto->getId() !== null, 'El producto debe tener ID después de crear');
        $this->assert($producto->getNombre() === 'Producto Test Simple', 'El nombre debe coincidir');
        $this->assert($producto->getSku() === 'TEST_SIMPLE_001', 'El SKU debe coincidir');
        $this->assert($producto->getActivo() === true, 'El producto debe estar activo por defecto');
        
        echo "✅ Test crear producto: PASÓ\n";
        return $producto;
    }

    public function testObtenerProducto()
    {
        echo "🧪 Test: Obtener producto...\n";
        
        $producto = $this->testCrearProducto();
        $productoService = $this->container->get('catalogo.service.producto');
        
        $productoObtenido = $productoService->obtenerPorId($producto->getId());
        
        $this->assert($productoObtenido->getId() === $producto->getId(), 'Los IDs deben coincidir');
        $this->assert($productoObtenido->getNombre() === $producto->getNombre(), 'Los nombres deben coincidir');
        
        echo "✅ Test obtener producto: PASÓ\n";
        return $productoObtenido;
    }

    public function testActualizarProducto()
    {
        echo "🧪 Test: Actualizar producto...\n";
        
        $producto = $this->testCrearProducto();
        $productoService = $this->container->get('catalogo.service.producto');
        
        $dtoUpdate = new ProductoDTO();
        $dtoUpdate->setNombre('Producto Actualizado Simple');
        $dtoUpdate->setPeso(1500);
        
        $productoActualizado = $productoService->actualizar($producto->getId(), $dtoUpdate);
        
        $this->assert($productoActualizado->getNombre() === 'Producto Actualizado Simple', 'El nombre debe haberse actualizado');
        $this->assert($productoActualizado->getPeso() == 1500, 'El peso debe haberse actualizado. Actual: ' . $productoActualizado->getPeso() . ', Esperado: 1500');
        $this->assert($productoActualizado->getSku() === 'TEST_SIMPLE_001', 'El SKU no debe cambiar');
        
        echo "✅ Test actualizar producto: PASÓ\n";
        return $productoActualizado;
    }

    public function testObtenerTodos()
    {
        echo "🧪 Test: Obtener todos los productos...\n";
        
        $this->testCrearProducto();
        $productoService = $this->container->get('catalogo.service.producto');
        
        $resultado = $productoService->obtenerTodos(1, 10, []);
        
        $this->assert(isset($resultado['productos']), 'Debe devolver array de productos');
        $this->assert(isset($resultado['total']), 'Debe devolver total');
        $this->assert($resultado['total'] >= 1, 'Debe haber al menos 1 producto');
        
        echo "✅ Test obtener todos: PASÓ\n";
    }

    public function testBusquedaConFiltros()
    {
        echo "🧪 Test: Búsqueda con filtros...\n";
        
        $this->testCrearProducto();
        $productoService = $this->container->get('catalogo.service.producto');
        
        // Test filtro por categoría
        $resultado = $productoService->obtenerTodos(1, 10, ['categoria' => 'secos']);
        $this->assert($resultado['total'] >= 1, 'Debe encontrar productos en categoría secos');
        
        // Test búsqueda por término
        $resultado = $productoService->obtenerTodos(1, 10, ['q' => 'Test Simple']);
        $this->assert($resultado['total'] >= 1, 'Debe encontrar productos por término de búsqueda');
        
        // Test filtro por SKU
        $resultado = $productoService->obtenerTodos(1, 10, ['sku' => 'TEST_SIMPLE_001']);
        $this->assert($resultado['total'] === 1, 'Debe encontrar exactamente 1 producto por SKU');
        
        echo "✅ Test búsqueda con filtros: PASÓ\n";
    }

    private function assert($condition, $message)
    {
        if (!$condition) {
            throw new \Exception("❌ Assertion failed: $message");
        }
    }

    public function runAll()
    {
        echo "🚀 Iniciando tests simples del ProductoService...\n\n";
        
        $this->setUp();
        
        try {
            $this->testCrearProducto();
            echo "\n";
            
            $this->setUp(); // Reset
            $this->testObtenerProducto();
            echo "\n";
            
            $this->setUp(); // Reset
            $this->testActualizarProducto();
            echo "\n";
            
            $this->setUp(); // Reset
            $this->testObtenerTodos();
            echo "\n";
            
            $this->setUp(); // Reset
            $this->testBusquedaConFiltros();
            echo "\n";
            
            echo "🎉 ¡Todos los tests del ProductoService pasaron correctamente!\n";
            
        } catch (\Exception $e) {
            echo "💥 Error en test: " . $e->getMessage() . "\n";
            echo "📍 Stack trace:\n" . $e->getTraceAsString() . "\n";
            return false;
        }
        
        return true;
    }
}

// Ejecutar si se llama directamente
if (isset($argv) && basename($argv[0]) === basename(__FILE__)) {
    $test = new SimpleProductoTest();
    $success = $test->runAll();
    exit($success ? 0 : 1);
}
