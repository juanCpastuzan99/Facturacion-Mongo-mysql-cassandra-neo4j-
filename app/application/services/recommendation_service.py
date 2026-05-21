from typing import List

from ...domain.ports.person_repository import PersonRepository
from ...domain.ports.recommendation_repository import RecommendationRepository


class RecommendationService:
    def __init__(
        self,
        recommendation_repo: RecommendationRepository,
        person_repo: PersonRepository,
    ) -> None:
        self._graph = recommendation_repo
        self._persons = person_repo

    def recommend(self, client_document: str, limit: int = 5) -> List[dict]:
        client = self._persons.find_by_document(client_document)
        if not client or client.role != "CLIENT":
            raise ValueError(f"client {client_document} not found")
        return self._graph.recommend_for_client(client_document, limit=limit)
