<?php

use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Debug\Debug;

// Configurar autoloader de Composer
$loader = require_once __DIR__.'/../vendor/autoload.php';

// Habilitar debug
Debug::enable();

// Incluir el kernel de la aplicación
require_once __DIR__.'/../app/AppKernel.php';

// Crear kernel en modo desarrollo
$kernel = new AppKernel('dev', true);

// Crear la request desde los superglobales
$request = Request::createFromGlobals();

// Procesar la request y generar response
$response = $kernel->handle($request);

// Enviar la response
$response->send();

// Terminar el kernel
$kernel->terminate($request, $response);
