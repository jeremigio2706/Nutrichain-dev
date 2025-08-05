<?php

namespace CatalogoBundle\Exception;

/**
 * Excepción para cuando ya existe un producto con el mismo SKU
 */
class DuplicateSkuException extends \Exception
{
    public function __construct(string $sku)
    {
        parent::__construct("Ya existe un producto con el SKU: $sku");
    }
}
