from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.invoice import Invoice


class InvoiceRepository(ABC):
    """Puerto del dominio para facturas y sus detalles."""

    @abstractmethod
    def save(self, invoice: Invoice) -> Invoice: ...

    @abstractmethod
    def find_by_id(self, invoice_id: int) -> Optional[Invoice]: ...

    @abstractmethod
    def find_all(self, client_document: Optional[str] = None) -> List[Invoice]: ...

    @abstractmethod
    def find_purchased_skus_by_client(self, client_document: str) -> List[str]: ...
