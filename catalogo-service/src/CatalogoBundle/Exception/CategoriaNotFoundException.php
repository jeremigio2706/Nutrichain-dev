<?php

namespace CatalogoBundle\Exception;

/**
 * Excepción lanzada cuando no se encuentra una categoría
 */
class CategoriaNotFoundException extends \Exception
{
    public function __construct(string $identifier, int $code = 0, \Throwable $previous = null)
    {
        $message = "Categoría no encontrada con identificador: {$identifier}";
        parent::__construct($message, $code, $previous);
    }

    /**
     * Crea una excepción para categoría no encontrada por ID
     */
    public static function forId(int $id): self
    {
        return new self("ID {$id}");
    }

    /**
     * Crea una excepción para categoría no encontrada por código
     */
    public static function forCodigo(string $codigo): self
    {
        return new self("código '{$codigo}'");
    }

    /**
     * Obtiene un mensaje formateado para respuesta JSON
     */
    public function getFormattedMessage(): array
    {
        return [
            'error' => 'CATEGORIA_NOT_FOUND',
            'message' => $this->getMessage(),
            'code' => $this->getCode()
        ];
    }
}
