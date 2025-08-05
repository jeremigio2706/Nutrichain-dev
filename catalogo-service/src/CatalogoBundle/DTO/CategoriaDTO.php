<?php

namespace CatalogoBundle\DTO;

use Symfony\Component\Validator\Constraints as Assert;
use Symfony\Component\Validator\Context\ExecutionContextInterface;

class CategoriaDTO
{
    /**
     * @Assert\NotBlank(message="El campo 'nombre' es obligatorio.", groups={"create"})
     * @Assert\Length(
     * min=3,
     * max=255,
     * minMessage="El nombre debe tener al menos {{ limit }} caracteres.",
     * maxMessage="El nombre no puede exceder los {{ limit }} caracteres.",
     * groups={"create", "update"}
     * )
     */
    public $nombre;

    /**
     * @Assert\NotBlank(message="El campo 'codigo' es obligatorio.", groups={"create"})
     * @Assert\Length(
     * min=3,
     * max=50,
     * minMessage="El código debe tener al menos {{ limit }} caracteres.",
     * maxMessage="El código no puede exceder los {{ limit }} caracteres.",
     * groups={"create", "update"}
     * )
     * @Assert\Regex(
     * pattern="/^[a-z0-9_]+$/",
     * message="El código solo puede contener letras minúsculas, números y guiones bajos.",
     * groups={"create", "update"}
     * )
     */
    public $codigo;

    /**
     * @Assert\Length(max=1000, maxMessage="La descripción no puede exceder los {{ limit }} caracteres.", groups={"create", "update"})
     */
    public $descripcion;

    /**
     * @Assert\Type(type="numeric", groups={"create", "update"})
     */
    public $temperaturaMin;

    /**
     * @Assert\Type(type="numeric", groups={"create", "update"})
     */
    public $temperaturaMax;

    /**
     * @Assert\Type(type="boolean", message="El campo 'activo' debe ser un valor booleano (true/false).", groups={"create", "update"})
     */
    public $activo;

    public function __construct(array $data = [])
    {
        $this->nombre = $data['nombre'] ?? null;
        $this->codigo = $data['codigo'] ?? null;
        $this->descripcion = $data['descripcion'] ?? null;
        $this->temperaturaMin = $data['temperaturaMin'] ?? null;
        $this->temperaturaMax = $data['temperaturaMax'] ?? null;
        $this->activo = isset($data['activo']) ? (bool)$data['activo'] : null;
    }

    /**
     * @Assert\Callback(groups={"create", "update"})
     */
    public function validate(ExecutionContextInterface $context)
    {
        if ($this->temperaturaMin !== null && $this->temperaturaMax !== null) {
            if ($this->temperaturaMin >= $this->temperaturaMax) {
                $context->buildViolation('La temperatura mínima no puede ser mayor o igual que la máxima.')
                    ->atPath('temperaturaMin')
                    ->addViolation();
            }
        }
    }
}
