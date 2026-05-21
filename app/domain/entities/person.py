from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class Person:
    """Entidad del dominio que representa una persona (cliente o empleado).

    Persistida en Cassandra. El rol distingue cliente de empleado.
    Los atributos sociodemográficos alimentan al motor de recomendaciones (Neo4j).
    """

    document: str
    first_name: str
    last_name: str
    role: str
    email: str
    phone: str
    birth_date: date
    gender: str
    stratum: int
    neighborhood: str
    municipality: str
    department: str
    id: UUID = field(default_factory=uuid4)
    salary: Optional[float] = None

    VALID_ROLES = ("CLIENT", "EMPLOYEE")
    VALID_GENDERS = ("M", "F", "OTHER")

    def __post_init__(self) -> None:
        if self.role not in self.VALID_ROLES:
            raise ValueError(f"role must be one of {self.VALID_ROLES}")
        if self.gender not in self.VALID_GENDERS:
            raise ValueError(f"gender must be one of {self.VALID_GENDERS}")
        if not 1 <= self.stratum <= 6:
            raise ValueError("stratum must be between 1 and 6")
        if self.role == "EMPLOYEE" and self.salary is None:
            raise ValueError("salary is required for employees")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
