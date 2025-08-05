<?php

namespace CatalogoBundle\Exception;

/**
 * Excepción base para errores de validación
 */
class ValidationException extends \Exception
{
    private $errors;

    public function __construct(array $errors, string $message = "Errores de validación", int $code = 0, \Throwable $previous = null)
    {
        $this->errors = $errors;
        parent::__construct($message, $code, $previous);
    }

    public function getErrors(): array
    {
        return $this->errors;
    }

    public function getFormattedErrors(): array
    {
        $formatted = [];
        foreach ($this->errors as $field => $messages) {
            if (is_array($messages)) {
                $formatted[$field] = implode(', ', $messages);
            } else {
                $formatted[$field] = $messages;
            }
        }
        return $formatted;
    }

    public function getFirstError(): ?string
    {
        if (empty($this->errors)) {
            return null;
        }

        $firstField = array_key_first($this->errors);
        $firstError = $this->errors[$firstField];
        
        return is_array($firstError) ? $firstError[0] : $firstError;
    }
}
