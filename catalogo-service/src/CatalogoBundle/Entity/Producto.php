<?php

namespace CatalogoBundle\Entity;

use Doctrine\ORM\Mapping as ORM;
use JMS\Serializer\Annotation as JMS;
use Symfony\Component\Validator\Constraints as Assert;

/**
 * @ORM\Entity(repositoryClass="CatalogoBundle\Repository\ProductoRepository")
 * @ORM\Table(name="productos")
 * @JMS\ExclusionPolicy("none")
 */
class Producto
{
    /**
     * @ORM\Id
     * @ORM\GeneratedValue(strategy="AUTO")
     * @ORM\Column(type="integer")
     * @JMS\Groups({"producto_detail", "producto_list"})
     */
    private $id;

    /**
     * @ORM\Column(type="string", length=255, nullable=false)
     * @Assert\NotBlank(message="El nombre es obligatorio")
     * @Assert\Length(max=255, maxMessage="El nombre no puede exceder 255 caracteres")
     * @JMS\Groups({"producto_detail", "producto_list"})
     */
    private $nombre;

    /**
     * @ORM\Column(type="string", length=100, nullable=false, unique=true)
     * @Assert\NotBlank(message="El SKU es obligatorio")
     * @Assert\Length(max=100, maxMessage="El SKU no puede exceder 100 caracteres")
     * @JMS\Groups({"producto_detail", "producto_list"})
     */
    private $sku;

    /**
     * @ORM\Column(name="unidad_medida", type="string", length=50, nullable=false)
     * @Assert\NotBlank(message="La unidad de medida es obligatoria")
     * @JMS\Groups({"producto_detail", "producto_list"})
     */
    private $unidadMedida;

    /**
     * @ORM\Column(type="decimal", precision=10, scale=2, nullable=false)
     * @Assert\NotBlank(message="El peso es obligatorio")
     * @Assert\GreaterThan(value=0, message="El peso debe ser mayor a 0")
     * @JMS\Groups({"producto_detail", "producto_list"})
     */
    private $peso;

    /**
     * @ORM\Column(type="string", length=50, nullable=false)
     * @Assert\NotBlank(message="La categoría es obligatoria")
     * @Assert\Choice(choices={"refrigerados", "secos", "congelados"}, message="Categoría inválida")
     * @JMS\Groups({"producto_detail", "producto_list"})
     */
    private $categoria;

    /**
     * @ORM\Column(type="string", length=500, nullable=true)
     * @JMS\Groups({"producto_detail"})
     */
    private $imagen;

    /**
     * @ORM\Column(type="text", nullable=true)
     * @JMS\Groups({"producto_detail"})
     */
    private $descripcion;

    /**
     * @ORM\Column(type="boolean", nullable=false, options={"default": true})
     * @JMS\Groups({"producto_detail", "producto_list"})
     */
    private $activo;

    /**
     * @ORM\Column(name="created_at", type="datetime", nullable=true)
     * @JMS\Groups({"producto_detail"})
     * @JMS\Type("DateTime<'Y-m-d H:i:s'>")
     */
    private $fechaCreacion;

    /**
     * @ORM\Column(name="updated_at", type="datetime", nullable=true)
     * @JMS\Groups({"producto_detail"})
     * @JMS\Type("DateTime<'Y-m-d H:i:s'>")
     */
    private $fechaActualizacion;

    public function __construct()
    {
        $this->activo = true;
        $this->fechaCreacion = new \DateTime();
    }

    /**
     * @JMS\PreSerialize
     */
    public function preSerialize()
    {
        // Método para preparar datos antes de serializar si es necesario
    }

    // Getters y Setters

    public function getId()
    {
        return $this->id;
    }

    public function getNombre()
    {
        return $this->nombre;
    }

    public function setNombre($nombre)
    {
        $this->nombre = $nombre;
        return $this;
    }

    public function getSku()
    {
        return $this->sku;
    }

    public function setSku($sku)
    {
        $this->sku = $sku;
        return $this;
    }

    public function getUnidadMedida()
    {
        return $this->unidadMedida;
    }

    public function setUnidadMedida($unidadMedida)
    {
        $this->unidadMedida = $unidadMedida;
        return $this;
    }

    public function getPeso()
    {
        return $this->peso;
    }

    public function setPeso($peso)
    {
        $this->peso = $peso;
        return $this;
    }

    public function getCategoria()
    {
        return $this->categoria;
    }

    public function setCategoria($categoria)
    {
        $this->categoria = $categoria;
        return $this;
    }

    public function getImagen()
    {
        return $this->imagen;
    }

    public function setImagen($imagen)
    {
        $this->imagen = $imagen;
        return $this;
    }

    public function getDescripcion()
    {
        return $this->descripcion;
    }

    public function setDescripcion($descripcion)
    {
        $this->descripcion = $descripcion;
        return $this;
    }

    public function getActivo()
    {
        return $this->activo;
    }

    public function setActivo($activo)
    {
        $this->activo = $activo;
        return $this;
    }

    public function getFechaCreacion()
    {
        return $this->fechaCreacion;
    }

    public function setFechaCreacion($fechaCreacion)
    {
        $this->fechaCreacion = $fechaCreacion;
        return $this;
    }

    public function getFechaActualizacion()
    {
        return $this->fechaActualizacion;
    }

    public function setFechaActualizacion($fechaActualizacion)
    {
        $this->fechaActualizacion = $fechaActualizacion;
        return $this;
    }

    /**
     * Convierte la entidad a array para respuestas JSON
     *
     * @return array
     */
    public function getJsonData()
    {
        return [
            'id' => $this->id,
            'nombre' => $this->nombre,
            'sku' => $this->sku,
            'unidad_medida' => $this->unidadMedida,
            'peso' => (float) $this->peso,
            'categoria' => $this->categoria,
            'imagen' => $this->imagen,
            'descripcion' => $this->descripcion,
            'activo' => $this->activo,
            'fecha_creacion' => $this->fechaCreacion ? $this->fechaCreacion->format('Y-m-d H:i:s') : null,
            'fecha_actualizacion' => $this->fechaActualizacion ? $this->fechaActualizacion->format('Y-m-d H:i:s') : null
        ];
    }

    /**
     * Método para validar datos antes de persistir
     *
     * @return array Array de errores si los hay
     */
    public function validate()
    {
        $errors = [];

        if (empty($this->nombre)) {
            $errors[] = 'El nombre es obligatorio';
        }

        if (empty($this->sku)) {
            $errors[] = 'El SKU es obligatorio';
        }

        if (empty($this->unidadMedida)) {
            $errors[] = 'La unidad de medida es obligatoria';
        }

        if ($this->peso <= 0) {
            $errors[] = 'El peso debe ser mayor a 0';
        }

        if (!in_array($this->categoria, ['refrigerados', 'secos', 'congelados'])) {
            $errors[] = 'La categoría debe ser: refrigerados, secos o congelados';
        }

        return $errors;
    }
}
