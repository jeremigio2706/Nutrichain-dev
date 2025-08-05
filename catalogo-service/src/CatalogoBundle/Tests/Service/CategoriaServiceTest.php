<?php

namespace CatalogoBundle\Tests\Service;

use CatalogoBundle\Tests\CatalogoBundleTestCase;
use CatalogoBundle\Service\CategoriaService;
use CatalogoBundle\DTO\CategoriaDTO;
use CatalogoBundle\Entity\Categoria;
use CatalogoBundle\Exception\CategoriaNotFoundException;
use CatalogoBundle\Exception\DuplicateCodigoCategoriaException;
use CatalogoBundle\Exception\ValidationException;

/**
 * Test unitarios para CategoriaService
 */
class CategoriaServiceTest extends CatalogoBundleTestCase
{
    /**
     * @var CategoriaService
     */
    private $categoriaService;

    /**
     * @var \Doctrine\ORM\EntityManagerInterface
     */
    private $em;

    protected function setUp(): void
    {
        parent::setUp();
        
        $this->categoriaService = $this->getService('catalogo.service.categoria');
        $this->em = $this->getEntityManager();
    }

    protected function tearDown(): void
    {
        parent::tearDown();
    }

    /**
     * Test: Crear categoría con datos válidos
     */
    public function testCrearCategoriaValida()
    {
        $dto = new CategoriaDTO([
            'codigo' => 'test001',
            'nombre' => 'Categoría Test Unitario',
            'descripcion' => 'Descripción de prueba para test unitario',
            'temperaturaMin' => 5.0,
            'temperaturaMax' => 25.0,
            'activo' => true
        ]);

        $categoria = $this->categoriaService->crear($dto);

        $this->assertInstanceOf(Categoria::class, $categoria);
        $this->assertEquals('test001', $categoria->getCodigo());
        $this->assertEquals('Categoría Test Unitario', $categoria->getNombre());
        $this->assertEquals('Descripción de prueba para test unitario', $categoria->getDescripcion());
        $this->assertEquals(5.0, $categoria->getTemperaturaMin());
        $this->assertEquals(25.0, $categoria->getTemperaturaMax());
        $this->assertTrue($categoria->isActivo());
        $this->assertNotNull($categoria->getId());

        // Limpiar
        $this->em->remove($categoria);
        $this->em->flush();
    }

    /**
     * Test: Crear categoría con código duplicado debe fallar
     */
    public function testCrearCategoriaConCodigoDuplicado()
    {
        // Crear primera categoría
        $dto1 = new CategoriaDTO([
            'codigo' => 'dupl001',
            'nombre' => 'Primera Categoría',
            'descripcion' => 'Primera descripción'
        ]);

        $categoria1 = $this->categoriaService->crear($dto1);

        // Intentar crear segunda categoría con mismo código
        $dto2 = new CategoriaDTO([
            'codigo' => 'dupl001',
            'nombre' => 'Segunda Categoría',
            'descripcion' => 'Segunda descripción'
        ]);

        $this->expectException(DuplicateCodigoCategoriaException::class);
        
        try {
            $this->categoriaService->crear($dto2);
        } finally {
            // Limpiar
            $this->em->remove($categoria1);
            $this->em->flush();
        }
    }

    /**
     * Test: Crear categoría sin campos obligatorios debe fallar
     */
    public function testCrearCategoriaSinCamposObligatorios()
    {
        $dto = new CategoriaDTO([
            'nombre' => 'Categoría Incompleta'
            // Falta código que es obligatorio
        ]);

        $this->expectException(ValidationException::class);
        $this->categoriaService->crear($dto);
    }

    /**
     * Test: Obtener categoría por ID existente
     */
    public function testObtenerCategoriaPorIdExistente()
    {
        // Crear categoría de prueba
        $dto = new CategoriaDTO([
            'codigo' => 'obtener001',
            'nombre' => 'Categoría Para Obtener',
            'descripcion' => 'Descripción de prueba'
        ]);

        $categoriaCreada = $this->categoriaService->crear($dto);
        $id = $categoriaCreada->getId();

        // Obtener la categoría
        $categoriaObtenida = $this->categoriaService->obtenerPorId($id);

        $this->assertEquals($id, $categoriaObtenida->getId());
        $this->assertEquals('obtener001', $categoriaObtenida->getCodigo());
        $this->assertEquals('Categoría Para Obtener', $categoriaObtenida->getNombre());

        // Limpiar
        $this->em->remove($categoriaCreada);
        $this->em->flush();
    }

    /**
     * Test: Obtener categoría por ID inexistente debe fallar
     */
    public function testObtenerCategoriaPorIdInexistente()
    {
        $idInexistente = 999999;

        $this->expectException(CategoriaNotFoundException::class);
        $this->categoriaService->obtenerPorId($idInexistente);
    }

    /**
     * Test: Obtener categoría inactiva con soloActivos=true debe fallar
     */
    public function testObtenerCategoriaInactivaConSoloActivosTrue()
    {
        // Crear categoría y desactivarla
        $dto = new CategoriaDTO([
            'codigo' => 'inactiva_solo_activos_' . time(),
            'nombre' => 'Categoría Inactiva',
            'descripcion' => 'Test categoría inactiva',
            'activo' => true
        ]);

        $categoria = $this->categoriaService->crear($dto);
        $id = $categoria->getId();

        // Desactivar la categoría
        $dtoUpdate = new CategoriaDTO([
            'activo' => false
        ]);
        $this->categoriaService->actualizar($id, $dtoUpdate);

        // Intentar obtener con soloActivos=true debe fallar
        $this->expectException(CategoriaNotFoundException::class);
        $this->categoriaService->obtenerPorId($id, true);

        // Limpiar
        $categoriaInactiva = $this->categoriaService->obtenerPorId($id, false);
        $this->em->remove($categoriaInactiva);
        $this->em->flush();
    }

    /**
     * Test: Obtener categoría inactiva con soloActivos=false debe funcionar
     */
    public function testObtenerCategoriaInactivaConSoloActivosFalse()
    {
        // Crear categoría y desactivarla
        $dto = new CategoriaDTO([
            'codigo' => 'inactiva002',
            'nombre' => 'Categoría Inactiva 2',
            'descripcion' => 'Test categoría inactiva 2'
        ]);

        $categoria = $this->categoriaService->crear($dto);
        $id = $categoria->getId();

        // Desactivar la categoría
        $dtoUpdate = new CategoriaDTO([
            'activo' => false
        ]);
        $this->categoriaService->actualizar($id, $dtoUpdate);

        // Obtener con soloActivos=false debe funcionar
        $categoriaObtenida = $this->categoriaService->obtenerPorId($id, false);
        
        $this->assertEquals($id, $categoriaObtenida->getId());
        $this->assertEquals('inactiva002', $categoriaObtenida->getCodigo());
        $this->assertFalse($categoriaObtenida->isActivo());

        // Limpiar
        $this->em->remove($categoriaObtenida);
        $this->em->flush();
    }

    /**
     * Test: Actualizar categoría existente
     */
    public function testActualizarCategoriaExistente()
    {
        // Crear categoría de prueba
        $dto = new CategoriaDTO([]);
        $dto->codigo = 'actualizar001';
        $dto->nombre = 'Categoría Original';
        $dto->descripcion = 'Descripción original';
        $dto->temperaturaMin = 0.0;
        $dto->temperaturaMax = 10.0;

        $categoria = $this->categoriaService->crear($dto);
        $id = $categoria->getId();

        // Actualizar categoría
        $dtoUpdate = new CategoriaDTO([]);
        $dtoUpdate->nombre = 'Categoría Actualizada';
        $dtoUpdate->descripcion = 'Descripción actualizada';
        $dtoUpdate->temperaturaMin = 5.0;
        $dtoUpdate->temperaturaMax = 15.0;

        $categoriaActualizada = $this->categoriaService->actualizar($id, $dtoUpdate);

        $this->assertEquals('Categoría Actualizada', $categoriaActualizada->getNombre());
        $this->assertEquals('Descripción actualizada', $categoriaActualizada->getDescripcion());
        $this->assertEquals(5.0, $categoriaActualizada->getTemperaturaMin());
        $this->assertEquals(15.0, $categoriaActualizada->getTemperaturaMax());
        $this->assertEquals('actualizar001', $categoriaActualizada->getCodigo()); // No debería cambiar

        // Limpiar
        $this->em->remove($categoriaActualizada);
        $this->em->flush();
    }

    /**
     * Test: Actualizar código de categoría
     */
    public function testActualizarCodigoCategoria()
    {
        // Crear categoría de prueba
        $dto = new CategoriaDTO([]);
        $dto->codigo = 'codigo_viejo';
        $dto->nombre = 'Categoría Test Código';
        $dto->descripcion = 'Test cambio de código';

        $categoria = $this->categoriaService->crear($dto);
        $id = $categoria->getId();

        // Actualizar código
        $dtoUpdate = new CategoriaDTO([]);
        $dtoUpdate->codigo = 'codigo_nuevo';

        $categoriaActualizada = $this->categoriaService->actualizar($id, $dtoUpdate);

        $this->assertEquals('codigo_nuevo', $categoriaActualizada->getCodigo());
        $this->assertEquals('Categoría Test Código', $categoriaActualizada->getNombre()); // No debería cambiar

        // Limpiar
        $this->em->remove($categoriaActualizada);
        $this->em->flush();
    }

    /**
     * Test: Actualizar código a uno que ya existe debe fallar
     */
    public function testActualizarCodigoADuplicadoDebaFallar()
    {
        // Crear primera categoría
        $dto1 = new CategoriaDTO([]);
        $dto1->codigo = 'existente001';
        $dto1->nombre = 'Primera Categoría';
        $categoria1 = $this->categoriaService->crear($dto1);

        // Crear segunda categoría
        $dto2 = new CategoriaDTO([]);
        $dto2->codigo = 'actualizar002';
        $dto2->nombre = 'Segunda Categoría';
        $categoria2 = $this->categoriaService->crear($dto2);

        // Intentar actualizar segunda categoría con código de la primera
        $dtoUpdate = new CategoriaDTO([]);
        $dtoUpdate->codigo = 'existente001';

        $this->expectException(DuplicateCodigoCategoriaException::class);

        try {
            $this->categoriaService->actualizar($categoria2->getId(), $dtoUpdate);
        } finally {
            // Limpiar
            $this->em->remove($categoria1);
            $this->em->remove($categoria2);
            $this->em->flush();
        }
    }

    /**
     * Test: Desactivar categoría
     */
    public function testDesactivarCategoria()
    {
        // Crear categoría de prueba
        $dto = new CategoriaDTO([]);
        $dto->codigo = 'desactivar001';
        $dto->nombre = 'Categoría Para Desactivar';
        $dto->descripcion = 'Test desactivación';

        $categoria = $this->categoriaService->crear($dto);
        $id = $categoria->getId();

        $this->assertTrue($categoria->isActivo());

        // Desactivar categoría
        $dtoUpdate = new CategoriaDTO([]);
        $dtoUpdate->activo = false;

        $categoriaDesactivada = $this->categoriaService->actualizar($id, $dtoUpdate);

        $this->assertFalse($categoriaDesactivada->isActivo());

        // Limpiar
        $this->em->remove($categoriaDesactivada);
        $this->em->flush();
    }

    /**
     * Test: Eliminar categoría permanentemente
     */
    public function testEliminarCategoriaPermanentemente()
    {
        // Crear categoría de prueba
        $dto = new CategoriaDTO([]);
        $dto->codigo = 'eliminar001';
        $dto->nombre = 'Categoría Para Eliminar';
        $dto->descripcion = 'Test eliminación';

        $categoria = $this->categoriaService->crear($dto);
        $id = $categoria->getId();

        // Verificar que existe
        $categoriaAntes = $this->categoriaService->obtenerPorId($id);
        $this->assertNotNull($categoriaAntes);

        // Eliminar categoría
        $this->categoriaService->eliminar($id);

        // Verificar que ya no existe
        $this->expectException(CategoriaNotFoundException::class);
        $this->categoriaService->obtenerPorId($id);
    }

    /**
     * Test: Obtener todas las categorías activas
     */
    public function testObtenerTodasCategoriasActivas()
    {
        // Crear categorías de prueba (activas e inactivas)
        $categoriasCreadas = [];
        
        // Crear 3 categorías activas
        for ($i = 1; $i <= 3; $i++) {
            $dto = new CategoriaDTO([]);
            $dto->codigo = "test_todas_act_$i";
            $dto->nombre = "Categoría Activa $i";
            $dto->descripcion = "Descripción $i";
            $dto->activo = true;

            $categoriasCreadas[] = $this->categoriaService->crear($dto);
        }

        // Crear 2 categorías inactivas
        for ($i = 1; $i <= 2; $i++) {
            $dto = new CategoriaDTO([]);
            $dto->codigo = "test_todas_inact_$i";
            $dto->nombre = "Categoría Inactiva $i";
            $dto->descripcion = "Descripción inactiva $i";
            $dto->activo = true; // Crear como activa primero

            $categoria = $this->categoriaService->crear($dto);
            $categoriasCreadas[] = $categoria;

            // Luego desactivar
            $dtoUpdate = new CategoriaDTO([]);
            $dtoUpdate->activo = false;
            $this->categoriaService->actualizar($categoria->getId(), $dtoUpdate);
        }

        // Obtener todas las categorías (solo activas)
        $categorias = $this->categoriaService->obtenerTodas();

        // Verificar que se obtuvieron categorías
        $this->assertTrue(is_array($categorias));
        
        // Contar cuántas de nuestras categorías de test están en el resultado
        $nuestrasCategoriasActivas = 0;
        $nuestrasCategoriasInactivas = 0;
        
        foreach ($categorias as $categoria) {
            if (strpos($categoria->getCodigo(), 'test_todas_act_') === 0) {
                $nuestrasCategoriasActivas++;
                $this->assertTrue($categoria->isActivo());
            }
            if (strpos($categoria->getCodigo(), 'test_todas_inact_') === 0) {
                $nuestrasCategoriasInactivas++;
            }
        }

        // Verificar que solo se obtuvieron las categorías activas
        $this->assertEquals(3, $nuestrasCategoriasActivas);
        $this->assertEquals(0, $nuestrasCategoriasInactivas);

        // Limpiar
        foreach ($categoriasCreadas as $categoria) {
            // Obtener la categoría actualizada para asegurar que tenemos la versión correcta
            $categoriaActual = $this->categoriaService->obtenerPorId($categoria->getId(), false);
            $this->em->remove($categoriaActual);
        }
        $this->em->flush();
    }

    /**
     * Test: Validación de temperaturas
     */
    public function testValidacionTemperaturas()
    {
        // Crear categoría con temperaturas válidas
        $dto = new CategoriaDTO([]);
        $dto->codigo = 'temp001';
        $dto->nombre = 'Categoría Temperatura';
        $dto->temperaturaMin = -10.5;
        $dto->temperaturaMax = 40.0;

        $categoria = $this->categoriaService->crear($dto);

        $this->assertEquals(-10.5, $categoria->getTemperaturaMin());
        $this->assertEquals(40.0, $categoria->getTemperaturaMax());

        // Limpiar
        $this->em->remove($categoria);
        $this->em->flush();
    }

    /**
     * Test: Crear categoría con datos mínimos requeridos
     */
    public function testCrearCategoriaConDatosMinimos()
    {
        $dto = new CategoriaDTO([]);
        $dto->codigo = 'min001';
        $dto->nombre = 'Categoría Mínima';
        // Solo campos obligatorios

        $categoria = $this->categoriaService->crear($dto);

        $this->assertEquals('min001', $categoria->getCodigo());
        $this->assertEquals('Categoría Mínima', $categoria->getNombre());
        $this->assertTrue($categoria->isActivo()); // Debería ser true por defecto
        $this->assertNotNull($categoria->getId());

        // Limpiar
        $this->em->remove($categoria);
        $this->em->flush();
    }

    /**
     * Test: Actualizar solo algunos campos
     */
    public function testActualizarSoloAlgunosCampos()
    {
        // Crear categoría completa
        $dto = new CategoriaDTO([]);
        $dto->codigo = 'parcial001';
        $dto->nombre = 'Nombre Original';
        $dto->descripcion = 'Descripción Original';
        $dto->temperaturaMin = 0.0;
        $dto->temperaturaMax = 20.0;

        $categoria = $this->categoriaService->crear($dto);
        $id = $categoria->getId();

        // Actualizar solo el nombre
        $dtoUpdate = new CategoriaDTO([]);
        $dtoUpdate->nombre = 'Nombre Actualizado';

        $categoriaActualizada = $this->categoriaService->actualizar($id, $dtoUpdate);

        // Verificar que solo el nombre cambió
        $this->assertEquals('Nombre Actualizado', $categoriaActualizada->getNombre());
        $this->assertEquals('parcial001', $categoriaActualizada->getCodigo());
        $this->assertEquals('Descripción Original', $categoriaActualizada->getDescripcion());
        $this->assertEquals(0.0, $categoriaActualizada->getTemperaturaMin());
        $this->assertEquals(20.0, $categoriaActualizada->getTemperaturaMax());

        // Limpiar
        $this->em->remove($categoriaActualizada);
        $this->em->flush();
    }
}