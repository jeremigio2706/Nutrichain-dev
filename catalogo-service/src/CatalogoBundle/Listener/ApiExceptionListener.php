<?php

namespace CatalogoBundle\Listener;

use Symfony\Component\HttpKernel\Event\GetResponseForExceptionEvent;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpKernel\Exception\HttpExceptionInterface;
use CatalogoBundle\Exception\CategoriaNotFoundException;
use CatalogoBundle\Exception\DuplicateCodigoCategoriaException;
use CatalogoBundle\Exception\ProductoNotFoundException;
use CatalogoBundle\Exception\DuplicateSkuException;
use CatalogoBundle\Exception\ValidationException;

class ApiExceptionListener
{
    private $debug;
    private $logger;

    public function __construct($debug = false, $logger = null)
    {
        $this->debug = $debug;
        $this->logger = $logger;
    }

    public function onKernelException(GetResponseForExceptionEvent $event)
    {
        $exception = $event->getException();
        $request = $event->getRequest();
        
        // Log detallado de la excepción
        if ($this->logger) {
            $this->logger->error('ApiExceptionListener: Excepción capturada', [
                'exception_class' => get_class($exception),
                'exception_message' => $exception->getMessage(),
                'exception_file' => $exception->getFile(),
                'exception_line' => $exception->getLine(),
                'request_uri' => $request->getRequestUri(),
                'request_method' => $request->getMethod(),
                'request_params' => $request->query->all(),
                'trace' => $this->debug ? $exception->getTraceAsString() : null
            ]);
        }
        
        $response = null;
        $data = [
            'success' => false,
        ];

        switch (true) {
            case $exception instanceof CategoriaNotFoundException:
                $data['error'] = 'NOT_FOUND';
                $data['message'] = $exception->getMessage();
                $statusCode = Response::HTTP_NOT_FOUND;
                break;

            case $exception instanceof ProductoNotFoundException:
                $data['error'] = 'NOT_FOUND';
                $data['message'] = $exception->getMessage();
                $statusCode = Response::HTTP_NOT_FOUND;
                break;

            case $exception instanceof DuplicateCodigoCategoriaException:
                $data['error'] = 'CONFLICT';
                $data['message'] = $exception->getMessage();
                $data['sugerencias'] = $exception->getSuggestedCodes();
                $statusCode = Response::HTTP_CONFLICT;
                break;

            case $exception instanceof DuplicateSkuException:
                $data['error'] = 'CONFLICT';
                $data['message'] = $exception->getMessage();
                $statusCode = Response::HTTP_CONFLICT;
                break;
            
            case $exception instanceof ValidationException:
                $data['error'] = 'VALIDATION_FAILED';
                $data['message'] = 'Los datos enviados son inválidos.';
                $data['details'] = $exception->getErrors();
                
                // Manejo especial para errores de validación de imágenes
                if ($this->esErrorValidacionImagen($exception)) {
                    $data['tipo_error'] = 'IMAGEN_INVALIDA';
                    $data['ayuda'] = [
                        'formatos_permitidos' => ['jpg', 'jpeg', 'png', 'gif', 'webp'],
                        'protocolo_requerido' => 'http/https',
                        'ejemplo' => 'https://ejemplo.com/imagen.jpg'
                    ];
                }
                
                $statusCode = Response::HTTP_BAD_REQUEST;
                break;

            case $exception instanceof HttpExceptionInterface:
                $data['message'] = $exception->getMessage();
                $statusCode = $exception->getStatusCode();
                break;

            default:
                $data['error'] = 'INTERNAL_SERVER_ERROR';
                $data['message'] = $this->debug ? $exception->getMessage() : 'Ha ocurrido un error inesperado.';
                if ($this->debug) {
                    $data['trace'] = $exception->getTraceAsString();
                }
                $statusCode = Response::HTTP_INTERNAL_SERVER_ERROR;
                break;
        }
        
        $event->setResponse(new JsonResponse($data, $statusCode));
    }

    /**
     * Verifica si es un error de validación de imagen
     */
    private function esErrorValidacionImagen(ValidationException $exception): bool
    {
        $errors = $exception->getErrors();
        
        // Buscar errores relacionados con 'imagen'
        if (isset($errors['imagen'])) {
            return true;
        }
        
        // Buscar mensajes que contengan términos relacionados con imágenes
        foreach ($errors as $field => $messages) {
            $mensajesTexto = is_array($messages) ? implode(' ', $messages) : $messages;
            if (stripos($mensajesTexto, 'imagen') !== false || 
                stripos($mensajesTexto, 'url') !== false ||
                stripos($mensajesTexto, 'jpg') !== false ||
                stripos($mensajesTexto, 'png') !== false) {
                return true;
            }
        }
        
        return false;
    }
}
