<?php

namespace CatalogoBundle\Entity;

use Doctrine\ORM\Mapping as ORM;
use JMS\Serializer\Annotation as JMS;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;

/**
 * @ORM\Entity(repositoryClass="CatalogoBundle\Repository\CategoriaRepository")
 * @ORM\Table(
 * name="categorias",
 * uniqueConstraints={@ORM\UniqueConstraint(name="categorias_codigo_key", columns={"codigo"})}
 * )
 * @ORM\HasLifecycleCallbacks()
 */
class Categoria
{
    /**
     * @ORM\Id
     * @ORM\GeneratedValue(strategy="IDENTITY")
     * @ORM\Column(type="integer")
     * @JMS\Groups({"categoria_list", "categoria_detail", "producto_detail"})
     */
    private $id;

    /**
     * @ORM\Column(type="string", length=50, nullable=false)
     * @JMS\Groups({"categoria_list", "categoria_detail"})
     */
    private $codigo;

    /**
     * @ORM\Column(type="string", length=255, nullable=false)
     * @JMS\Groups({"categoria_list", "categoria_detail", "producto_detail"})
     */
    private $nombre;

    /**
     * @ORM\Column(type="text", nullable=true)
     * @JMS\Groups({"categoria_detail"})
     */
    private $descripcion;

    /**
     * @ORM\Column(name="temperatura_min", type="decimal", precision=5, scale=2, nullable=true)
     * @JMS\Groups({"categoria_detail"})
     * @JMS\SerializedName("temperaturaMinima")
     */
    private $temperaturaMin;

    /**
     * @ORM\Column(name="temperatura_max", type="decimal", precision=5, scale=2, nullable=true)
     * @JMS\Groups({"categoria_detail"})
     * @JMS\SerializedName("temperaturaMaxima")
     */
    private $temperaturaMax;

    /**
     * @ORM\Column(type="boolean", options={"default": true})
     * @JMS\Groups({"categoria_list", "categoria_detail"})
     */
    private $activo;

    /**
     * @ORM\Column(name="created_at", type="datetime")
     * @JMS\Groups({"categoria_list", "categoria_detail"})
     * @JMS\Type("DateTime<'Y-m-d H:i:s'>")
     * @JMS\SerializedName("fechaCreacion")
     */
    private $fechaCreacion;

    /**
     * @ORM\Column(name="updated_at", type="datetime", nullable=true)
     * @JMS\Groups({"categoria_list", "categoria_detail"})
     * @JMS\Type("DateTime<'Y-m-d H:i:s'>")
     * @JMS\SerializedName("fechaActualizacion")
     */
    private $fechaActualizacion;

    /**
     * @ORM\OneToMany(targetEntity="Producto", mappedBy="categoria")
     * @JMS\Exclude // Excluimos para evitar referencias circulares en la serialización
     */
    private $productos;

    public function __construct()
    {
        $this->activo = true;
        $this->fechaCreacion = new \DateTime();
        $this->productos = new ArrayCollection();
    }

    /**
     * @ORM\PreUpdate
     */
    public function onPreUpdate()
    {
        $this->fechaActualizacion = new \DateTime();
    }

    // --- Getters y Setters (con tipado estricto) ---

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getCodigo(): ?string
    {
        return $this->codigo;
    }

    public function setCodigo(string $codigo): self
    {
        $this->codigo = $codigo;
        return $this;
    }

    public function getNombre(): ?string
    {
        return $this->nombre;
    }

    public function setNombre(string $nombre): self
    {
        $this->nombre = $nombre;
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

    public function getTemperaturaMin()
    {
        return $this->temperaturaMin;
    }

    public function setTemperaturaMin($temperaturaMin): self
    {
        $this->temperaturaMin = $temperaturaMin;
        return $this;
    }

    public function getTemperaturaMax()
    {
        return $this->temperaturaMax;
    }

    public function setTemperaturaMax($temperaturaMax): self
    {
        $this->temperaturaMax = $temperaturaMax;
        return $this;
    }

    public function isActivo(): ?bool
    {
        return $this->activo;
    }

    public function setActivo(bool $activo): self
    {
        $this->activo = $activo;
        return $this;
    }

    public function getFechaCreacion(): ?\DateTimeInterface
    {
        return $this->fechaCreacion;
    }
    
    public function getFechaActualizacion(): ?\DateTimeInterface
    {
        return $this->fechaActualizacion;
    }

    /**
     * @return Collection|Producto[]
     */
    public function getProductos(): Collection
    {
        return $this->productos;
    }
}
