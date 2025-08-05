<?php

namespace CatalogoBundle\Validator\Constraints;

use Symfony\Component\Validator\Constraint;
use Symfony\Component\Validator\ConstraintValidator;

/**
 * Validador para URLs de imágenes
 */
class ImageUrlValidator extends ConstraintValidator
{
    public function validate($value, Constraint $constraint)
    {
        if (null === $value || '' === $value) {
            return;
        }

        // Verificar que sea una URL válida
        if (!filter_var($value, FILTER_VALIDATE_URL)) {
            $this->context->buildViolation($constraint->invalidUrlMessage)
                ->addViolation();
            return;
        }

        $url = parse_url($value);
        
        // Verificar protocolo
        if (!isset($url['scheme']) || !in_array($url['scheme'], ['http', 'https'])) {
            $this->context->buildViolation($constraint->invalidUrlMessage)
                ->addViolation();
            return;
        }

        // Si se requiere HTTPS
        if ($constraint->requireHttps && $url['scheme'] !== 'https') {
            $this->context->buildViolation('La imagen debe usar protocolo HTTPS')
                ->addViolation();
            return;
        }

        // Verificar que tiene una extensión de imagen válida
        $path = $url['path'] ?? '';
        $extension = strtolower(pathinfo($path, PATHINFO_EXTENSION));
        
        if (empty($extension) || !in_array($extension, $constraint->allowedExtensions)) {
            $this->context->buildViolation($constraint->invalidExtensionMessage)
                ->addViolation();
            return;
        }

        // Verificar que no es una URL sospechosa
        $host = $url['host'] ?? '';
        if (empty($host)) {
            $this->context->buildViolation($constraint->invalidUrlMessage)
                ->addViolation();
            return;
        }

        // Verificar que no es localhost o IP local (opcional, para producción)
        if (in_array($host, ['localhost', '127.0.0.1', '0.0.0.0']) || 
            preg_match('/^192\.168\./', $host) || 
            preg_match('/^10\./', $host) || 
            preg_match('/^172\.(1[6-9]|2[0-9]|3[0-1])\./', $host)) {
            // En desarrollo permitir localhost
            if (getenv('APP_ENV') !== 'dev') {
                $this->context->buildViolation('No se permiten URLs locales para imágenes')
                    ->addViolation();
                return;
            }
        }
    }
}
