<?php

namespace CatalogoBundle\Exception;

/**
 * Excepción lanzada cuando se intenta crear o actualizar una categoría con un código que ya existe
 */
class DuplicateCodigoCategoriaException extends \Exception
{
    private $codigo;

    public function __construct(string $codigo, int $code = 0, \Throwable $previous = null)
    {
        $this->codigo = $codigo;
        $message = "Ya existe una categoría con el código: {$codigo}";
        parent::__construct($message, $code, $previous);
    }

    /**
     * Obtiene el código duplicado
     */
    public function getCodigo(): string
    {
        return $this->codigo;
    }

    /**
     * Obtiene un mensaje formateado para respuesta JSON
     */
    public function getFormattedMessage(): array
    {
        return [
            'error' => 'DUPLICATE_CATEGORIA_CODIGO',
            'message' => $this->getMessage(),
            'codigo' => $this->codigo
        ];
    }

    /**
     * Obtiene sugerencias de códigos alternativos
     */
    public function getSuggestedCodes(): array
    {
        $base = $this->codigo;
        $suggestions = [];
        
        // Generar códigos alternativos
        for ($i = 1; $i <= 3; $i++) {
            $suggestions[] = $base . '_' . $i;
            $suggestions[] = $base . $i;
        }
        
        return $suggestions;
    }
}
