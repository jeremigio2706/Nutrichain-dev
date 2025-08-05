<?php

namespace CatalogoBundle\Tests;

use Symfony\Bundle\FrameworkBundle\Test\WebTestCase;
use Symfony\Component\DependencyInjection\ContainerInterface;

/**
 * Clase base para tests de CatalogoBundle
 */
abstract class CatalogoBundleTestCase extends WebTestCase
{
    /**
     * @var ContainerInterface
     */
    protected $container;

    /**
     * @var \Symfony\Bundle\FrameworkBundle\Client
     */
    protected $client;

    protected function setUp(): void
    {
        parent::setUp();
        
        $this->client = static::createClient(['environment' => 'test']);
        $this->container = $this->client->getContainer();
        
        // Preparar base de datos de test
        $this->setupTestDatabase();
    }

    protected function tearDown(): void
    {
        parent::tearDown();
        
        $this->container = null;
        $this->client = null;
    }

    /**
     * Configurar base de datos de test
     */
    protected function setupTestDatabase()
    {
        $em = $this->getEntityManager();
        $schemaTool = new \Doctrine\ORM\Tools\SchemaTool($em);
        $metadata = $em->getMetadataFactory()->getAllMetadata();
        
        // Crear esquema si no existe
        try {
            $schemaTool->createSchema($metadata);
        } catch (\Exception $e) {
            // El esquema ya existe, continuar
        }
    }

    /**
     * Obtiene un servicio del contenedor
     */
    protected function getService($serviceId)
    {
        return $this->container->get($serviceId);
    }

    /**
     * Obtiene el Entity Manager
     */
    protected function getEntityManager()
    {
        return $this->container->get('doctrine.orm.entity_manager');
    }

    /**
     * Obtiene el logger
     */
    protected function getLogger()
    {
        return $this->container->get('logger');
    }

    /**
     * Obtiene el validador
     */
    protected function getValidator()
    {
        return $this->container->get('validator');
    }
}
