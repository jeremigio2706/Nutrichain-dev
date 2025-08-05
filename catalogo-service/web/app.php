<?php

use Symfony\Component\HttpFoundation\Request;

// Configurar autoloader de Composer
$loader = require_once __DIR__.'/../vendor/autoload.php';

// Incluir el kernel de la aplicación
require_once __DIR__.'/../app/AppKernel.php';

// Crear kernel en modo producción
$kernel = new AppKernel('prod', false);

// Cargar el archivo de clases optimizado
//$kernel->loadClassCache();

// Crear la request desde los superglobales
$request = Request::createFromGlobals();

// Procesar la request y generar response
$response = $kernel->handle($request);

// Enviar la response
$response->send();

// Terminar el kernel
$kernel->terminate($request, $response);
