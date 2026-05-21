from datetime import date
from typing import List, Optional

from cassandra.query import SimpleStatement

from ....domain.entities.person import Person
from ....domain.ports.person_repository import PersonRepository
from .cassandra_connection import CassandraConnection


class CassandraPersonRepository(PersonRepository):
    """Adaptador Cassandra para personas (clientes y empleados).

    Modelo: tabla person con PK por document. Una segunda tabla
    person_by_role permite listar por rol sin ALLOW FILTERING.
    """

    def __init__(self) -> None:
        self._session = CassandraConnection.session()

    def save(self, person: Person) -> Person:
        self._session.execute(
            """
            INSERT INTO person (
                document, id, first_name, last_name, role, email, phone,
                birth_date, gender, stratum, neighborhood, municipality,
                department, salary
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                person.document,
                person.id,
                person.first_name,
                person.last_name,
                person.role,
                person.email,
                person.phone,
                person.birth_date,
                person.gender,
                person.stratum,
                person.neighborhood,
                person.municipality,
                person.department,
                person.salary,
            ),
        )
        self._session.execute(
            """
            INSERT INTO person_by_role (role, document, first_name, last_name, email)
            VALUES (%s,%s,%s,%s,%s)
            """,
            (person.role, person.document, person.first_name, person.last_name, person.email),
        )
        return person

    def find_by_document(self, document: str) -> Optional[Person]:
        row = self._session.execute(
            "SELECT * FROM person WHERE document = %s", (document,)
        ).one()
        return self._row_to_person(row) if row else None

    def find_all(self, role: Optional[str] = None) -> List[Person]:
        if role:
            rows = self._session.execute(
                "SELECT document FROM person_by_role WHERE role = %s", (role,)
            )
            docs = [r.document for r in rows]
            return [p for p in (self.find_by_document(d) for d in docs) if p]
        rows = self._session.execute(SimpleStatement("SELECT * FROM person", fetch_size=500))
        return [self._row_to_person(r) for r in rows]

    def delete(self, document: str) -> None:
        person = self.find_by_document(document)
        if not person:
            return
        self._session.execute("DELETE FROM person WHERE document = %s", (document,))
        self._session.execute(
            "DELETE FROM person_by_role WHERE role = %s AND document = %s",
            (person.role, document),
        )

    @staticmethod
    def _row_to_person(row) -> Person:
        birth = row.birth_date
        if hasattr(birth, "date"):
            birth = birth.date()
        if not isinstance(birth, date):
            birth = date.fromisoformat(str(birth))
        return Person(
            id=row.id,
            document=row.document,
            first_name=row.first_name,
            last_name=row.last_name,
            role=row.role,
            email=row.email,
            phone=row.phone,
            birth_date=birth,
            gender=row.gender,
            stratum=row.stratum,
            neighborhood=row.neighborhood,
            municipality=row.municipality,
            department=row.department,
            salary=row.salary,
        )
