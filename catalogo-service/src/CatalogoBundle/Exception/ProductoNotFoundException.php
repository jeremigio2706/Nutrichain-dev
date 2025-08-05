<?php

namespace CatalogoBundle\Exception;

/**
 * Excepción para cuando un producto no es encontrado
 */
class ProductoNotFoundException extends \Exception
{
    public function __construct(string $identifier, string $type = 'ID')
    {
        parent::__construct("Producto no encontrado con $type: $identifier");
    }
}
