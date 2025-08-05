<?php

namespace CatalogoBundle\Tests\Simple;

use CatalogoBundle\Service\CategoriaService;
use CatalogoBundle\DTO\CategoriaDTO;

echo "📝 Iniciando SimpleCategoriaTest.php\n";

/**
 * Test simple para verificar funcionalidad básica de categorías
 */
class SimpleCategoriaTest
{
    private $container;
    private $kernel;

    public function __construct()
    {
        echo "🔧 Configurando kernel de Symfony...\n";
        // Configurar kernel de Symfony manualmente
        require_once '/var/www/html/app/bootstrap.php.cache';
        require_once '/var/www/html/app/AppKernel.php';
        
        $this->kernel = new \AppKernel('test', false);
        $this->kernel->boot();
        $this->container = $this->kernel->getContainer();
        echo "✅ Kernel configurado correctamente\n";
    }

    public function setUp()
    {
        // Configurar base de datos de test
        $em = $this->container->get('doctrine.orm.entity_manager');
        
        try {
            // Limpiar datos existentes de manera más simple
            $connection = $em->getConnection();
            $connection->exec('DELETE FROM categorias');
            // Reiniciar secuencias
            $connection->exec('ALTER SEQUENCE categorias_id_seq RESTART WITH 1');
        } catch (\Exception $e) {
            echo "⚠️  Advertencia: No se pudo limpiar categorías: " . $e->getMessage() . "\n";
        }
    }

    public function testCrearCategoria()
    {
        echo "🧪 Test: Crear categoría...\n";
        
        $categoriaService = $this->container->get('catalogo.service.categoria');
        
        $dto = new CategoriaDTO([
            'nombre' => 'Categoría Test Simple',
            'codigo' => 'categoria_test_simple',
            'descripcion' => 'Test simple de creación de categoría'
        ]);
        
        $categoria = $categoriaService->crear($dto);
        
        $this->assert($categoria->getId() !== null, 'La categoría debe tener ID después de crear');
        $this->assert($categoria->getNombre() === 'Categoría Test Simple', 'El nombre debe coincidir');
        $this->assert($categoria->getCodigo() === 'categoria_test_simple', 'El código debe coincidir');
        $this->assert($categoria->isActivo() === true, 'La categoría debe estar activa por defecto');
        
        echo "✅ Test crear categoría: PASÓ\n";
        return $categoria;
    }

    public function testObtenerCategoria()
    {
        echo "🧪 Test: Obtener categoría...\n";
        
        $categoria = $this->testCrearCategoria();
        $categoriaService = $this->container->get('catalogo.service.categoria');
        
        $categoriaObtenida = $categoriaService->obtenerPorId($categoria->getId());
        
        $this->assert($categoriaObtenida->getId() === $categoria->getId(), 'Los IDs deben coincidir');
        $this->assert($categoriaObtenida->getNombre() === $categoria->getNombre(), 'Los nombres deben coincidir');
        
        echo "✅ Test obtener categoría: PASÓ\n";
        return $categoriaObtenida;
    }

    public function testActualizarCategoria()
    {
        echo "🧪 Test: Actualizar categoría...\n";
        
        $categoria = $this->testCrearCategoria();
        $categoriaService = $this->container->get('catalogo.service.categoria');
        
        $dtoUpdate = new CategoriaDTO([
            'nombre' => 'Categoría Actualizada Simple',
            'descripcion' => 'Descripción actualizada'
        ]);
        
        $categoriaActualizada = $categoriaService->actualizar($categoria->getId(), $dtoUpdate);
        
        $this->assert($categoriaActualizada->getNombre() === 'Categoría Actualizada Simple', 'El nombre debe haberse actualizado');
        $this->assert($categoriaActualizada->getDescripcion() === 'Descripción actualizada', 'La descripción debe haberse actualizada');
        $this->assert($categoriaActualizada->getCodigo() === 'categoria_test_simple', 'El código no debe cambiar');
        
        echo "✅ Test actualizar categoría: PASÓ\n";
        return $categoriaActualizada;
    }

    public function testDesactivarCategoria()
    {
        echo "🧪 Test: Desactivar categoría...\n";
        
        $categoria = $this->testCrearCategoria();
        $categoriaService = $this->container->get('catalogo.service.categoria');
        
        $this->assert($categoria->isActivo() === true, 'La categoría debe estar activa inicialmente');
        
        $dtoUpdate = new CategoriaDTO([
            'activo' => false
        ]);
        
        $categoriaDesactivada = $categoriaService->actualizar($categoria->getId(), $dtoUpdate);
        
        $this->assert($categoriaDesactivada->isActivo() === false, 'La categoría debe estar desactivada');
        
        echo "✅ Test desactivar categoría: PASÓ\n";
        return $categoriaDesactivada;
    }

    public function testObtenerTodas()
    {
        echo "🧪 Test: Obtener todas las categorías...\n";
        
        $this->testCrearCategoria();
        $categoriaService = $this->container->get('catalogo.service.categoria');
        
        $categorias = $categoriaService->obtenerTodas();
        
        $this->assert(is_array($categorias), 'Debe devolver array de categorías');
        $this->assert(count($categorias) >= 1, 'Debe haber al menos 1 categoría');
        
        echo "✅ Test obtener todas: PASÓ\n";
    }

    private function assert($condition, $message)
    {
        if (!$condition) {
            throw new \Exception("❌ Assertion failed: $message");
        }
    }

    public function runAll()
    {
        echo "🚀 Iniciando tests simples del CategoriaService...\n\n";
        
        try {
            $this->setUp();
            $this->testCrearCategoria();
            echo "\n";
            
            $this->setUp();
            $this->testObtenerCategoria();
            echo "\n";
            
            $this->setUp();
            $this->testActualizarCategoria();
            echo "\n";
            
            $this->setUp();
            $this->testDesactivarCategoria();
            echo "\n";
            
            $this->setUp();
            $this->testObtenerTodas();
            echo "\n";
            
            echo "🎉 ¡Todos los tests del CategoriaService pasaron correctamente!\n";
            
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
    echo "🚀 Ejecutando SimpleCategoriaTest desde línea de comandos\n";
    $test = new SimpleCategoriaTest();
    $success = $test->runAll();
    echo "🏁 Test completado con resultado: " . ($success ? "ÉXITO" : "FALLO") . "\n";
    exit($success ? 0 : 1);
}
