from typing import List, Optional

from ...domain.entities.person import Person
from ...domain.ports.person_repository import PersonRepository
from ...domain.ports.recommendation_repository import RecommendationRepository


class PersonService:
    def __init__(
        self,
        person_repo: PersonRepository,
        recommendation_repo: RecommendationRepository,
    ) -> None:
        self._persons = person_repo
        self._graph = recommendation_repo

    def create(self, person: Person) -> Person:
        if self._persons.find_by_document(person.document):
            raise ValueError(f"Person with document {person.document} already exists")
        saved = self._persons.save(person)
        self._graph.upsert_person(saved)
        return saved

    def update(self, person: Person) -> Person:
        if not self._persons.find_by_document(person.document):
            raise ValueError(f"Person with document {person.document} not found")
        self._persons.save(person)
        self._graph.upsert_person(person)
        return person

    def get(self, document: str) -> Optional[Person]:
        return self._persons.find_by_document(document)

    def list(self, role: Optional[str] = None) -> List[Person]:
        return self._persons.find_all(role=role)

    def delete(self, document: str) -> None:
        self._persons.delete(document)
