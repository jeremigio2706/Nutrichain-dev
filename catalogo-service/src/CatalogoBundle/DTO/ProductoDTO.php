<?php

namespace CatalogoBundle\DTO;

use Symfony\Component\Validator\Constraints as Assert;
use CatalogoBundle\Validator\Constraints as CatalogoBundleAssert;

/**
 * DTO unificado para operaciones de productos (crear y actualizar)
 * Coincide exactamente con la estructura de la tabla productos
 */
class ProductoDTO
{
    /**
     * @Assert\Length(
     *     min=3,
     *     max=255,
     *     minMessage="El nombre debe tener al menos {{ limit }} caracteres",
     *     maxMessage="El nombre no puede tener más de {{ limit }} caracteres"
     * )
     */
    private $nombre;

    /**
     * @Assert\Length(
     *     min=3,
     *     max=100,
     *     minMessage="El SKU debe tener al menos {{ limit }} caracteres",
     *     maxMessage="El SKU no puede tener más de {{ limit }} caracteres"
     * )
     * @Assert\Regex(
     *     pattern="/^[A-Z0-9_-]+$/i",
     *     message="El SKU solo puede contener letras, números, guiones y guiones bajos"
     * )
     */
    private $sku;

    /**
     * @Assert\Choice(
     *     choices={"kg", "litro", "unidad", "docena", "gramo", "ml"},
     *     message="La unidad de medida debe ser una de: {{ choices }}"
     * )
     */
    private $unidadMedida;

    /**
     * @Assert\Type(
     *     type="numeric",
     *     message="El peso debe ser un número"
     * )
     * @Assert\GreaterThan(
     *     value=0,
     *     message="El peso debe ser mayor a 0"
     * )
     */
    private $peso;

    /**
     * @Assert\Choice(
     *     choices={"refrigerados", "secos", "congelados"},
     *     message="La categoría debe ser una de: {{ choices }}"
     * )
     */
    private $categoria;

    /**
     * @Assert\Length(
     *     max=500,
     *     maxMessage="La URL de imagen no puede tener más de {{ limit }} caracteres"
     * )
     * @CatalogoBundleAssert\ImageUrl
     */
    private $imagen;

    /**
     * @Assert\Length(
     *     max=1000,
     *     maxMessage="La descripción no puede tener más de {{ limit }} caracteres"
     * )
     */
    private $descripcion;

    /**
     * @Assert\Type(
     *     type="bool",
     *     message="El campo activo debe ser verdadero o falso"
     * )
     */
    private $activo;

    // Getters y Setters

    public function getNombre(): ?string
    {
        return $this->nombre;
    }

    public function setNombre(?string $nombre): self
    {
        $this->nombre = $nombre;
        return $this;
    }

    public function getSku(): ?string
    {
        return $this->sku;
    }

    public function setSku(?string $sku): self
    {
        $this->sku = $sku ? strtoupper(trim($sku)) : null;
        return $this;
    }

    public function getUnidadMedida(): ?string
    {
        return $this->unidadMedida;
    }

    public function setUnidadMedida(?string $unidadMedida): self
    {
        $this->unidadMedida = $unidadMedida;
        return $this;
    }

    public function getPeso(): ?float
    {
        return $this->peso;
    }

    public function setPeso(?float $peso): self
    {
        $this->peso = $peso;
        return $this;
    }

    public function getCategoria(): ?string
    {
        return $this->categoria;
    }

    public function setCategoria(?string $categoria): self
    {
        $this->categoria = $categoria;
        return $this;
    }

    public function getImagen(): ?string
    {
        return $this->imagen;
    }

    public function setImagen(?string $imagen): self
    {
        $this->imagen = $imagen;
        return $this;
    }

    public function getDescripcion(): ?string
    {
        return $this->descripcion;
    }

    public function setDescripcion(?string $descripcion): self
    {
        $this->descripcion = $descripcion;
        return $this;
    }

    public function getActivo(): ?bool
    {
        return $this->activo;
    }

    public function setActivo(?bool $activo): self
    {
        $this->activo = $activo;
        return $this;
    }

    /**
     * Crea un DTO desde un array de datos
     */
    public static function fromArray(array $data): self
    {
        $dto = new self();
        
        if (isset($data['nombre'])) {
            $dto->setNombre($data['nombre']);
        }
        
        if (isset($data['sku'])) {
            $dto->setSku($data['sku']);
        }
        
        if (isset($data['unidad_medida'])) {
            $dto->setUnidadMedida($data['unidad_medida']);
        }
        
        if (isset($data['peso'])) {
            $dto->setPeso((float) $data['peso']);
        }
        
        if (isset($data['categoria'])) {
            $dto->setCategoria($data['categoria']);
        }
        
        if (isset($data['descripcion'])) {
            $dto->setDescripcion($data['descripcion']);
        }
        
        if (isset($data['imagen'])) {
            $dto->setImagen($data['imagen']);
        }
        
        if (isset($data['activo'])) {
            $dto->setActivo((bool) $data['activo']);
        }

        return $dto;
    }

    /**
     * Convierte el DTO a array para compatibilidad
     */
    public function toArray(): array
    {
        $data = [];
        
        if ($this->nombre !== null) {
            $data['nombre'] = $this->nombre;
        }
        
        if ($this->sku !== null) {
            $data['sku'] = $this->sku;
        }
        
        if ($this->unidadMedida !== null) {
            $data['unidad_medida'] = $this->unidadMedida;
        }
        
        if ($this->peso !== null) {
            $data['peso'] = $this->peso;
        }
        
        if ($this->categoria !== null) {
            $data['categoria'] = $this->categoria;
        }
        
        if ($this->descripcion !== null) {
            $data['descripcion'] = $this->descripcion;
        }
        
        if ($this->imagen !== null) {
            $data['imagen'] = $this->imagen;
        }
        
        if ($this->activo !== null) {
            $data['activo'] = $this->activo;
        }

        return $data;
    }

    /**
     * Valida si es una operación de creación (campos obligatorios presentes)
     */
    public function esCreacion(): bool
    {
        return $this->nombre !== null && 
               $this->sku !== null && 
               $this->unidadMedida !== null && 
               $this->peso !== null &&
               $this->categoria !== null;
    }

    /**
     * Retorna las validaciones requeridas para creación
     */
    public function getValidacionesCreacion(): array
    {
        return [
            'nombre' => 'NotBlank',
            'sku' => 'NotBlank', 
            'unidad_medida' => 'NotBlank',
            'peso' => 'NotBlank',
            'categoria' => 'NotBlank'
        ];
    }

    /**
     * Verifica si tiene cambios para actualización
     */
    public function hasChanges(): bool
    {
        return $this->nombre !== null || 
               $this->sku !== null || 
               $this->unidadMedida !== null ||
               $this->peso !== null ||
               $this->categoria !== null ||
               $this->descripcion !== null ||
               $this->imagen !== null ||
               $this->activo !== null;
    }
}
