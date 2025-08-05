<?php

namespace CatalogoBundle\Validator\Constraints;

use Symfony\Component\Validator\Constraint;

/**
 * Validador personalizado para URLs de imágenes
 * 
 * @Annotation
 */
class ImageUrl extends Constraint
{
    public $message = 'La imagen debe ser una URL válida que apunte a un archivo de imagen (jpg, jpeg, png, gif, webp)';
    public $invalidUrlMessage = 'La imagen debe ser una URL válida';
    public $invalidExtensionMessage = 'La imagen debe tener una extensión válida (jpg, jpeg, png, gif, webp)';
    public $allowedExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp'];
    public $requireHttps = false;
}
