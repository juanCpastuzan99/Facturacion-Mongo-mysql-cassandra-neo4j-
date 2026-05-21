from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.person import Person


class PersonRepository(ABC):
    """Puerto del dominio para personas (clientes y empleados)."""

    @abstractmethod
    def save(self, person: Person) -> Person: ...

    @abstractmethod
    def find_by_document(self, document: str) -> Optional[Person]: ...

    @abstractmethod
    def find_all(self, role: Optional[str] = None) -> List[Person]: ...

    @abstractmethod
    def delete(self, document: str) -> None: ...
