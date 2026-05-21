from typing import List, Optional

from ...domain.entities.invoice import Invoice
from ...domain.entities.invoice_detail import InvoiceDetail
from ...domain.ports.invoice_repository import InvoiceRepository
from ...domain.ports.person_repository import PersonRepository
from ...domain.ports.product_repository import ProductRepository
from ...domain.ports.recommendation_repository import RecommendationRepository


class InvoiceService:
    """Orquesta la creación de facturas validando contra los 4 SGBDs."""

    def __init__(
        self,
        invoice_repo: InvoiceRepository,
        product_repo: ProductRepository,
        person_repo: PersonRepository,
        recommendation_repo: RecommendationRepository,
    ) -> None:
        self._invoices = invoice_repo
        self._products = product_repo
        self._persons = person_repo
        self._graph = recommendation_repo

    def create(
        self,
        client_document: str,
        employee_document: str,
        payment_method: str,
        items: List[dict],
    ) -> Invoice:
        """items: lista de {sku, quantity}."""
        client = self._persons.find_by_document(client_document)
        if not client or client.role != "CLIENT":
            raise ValueError(f"client {client_document} not found")
        employee = self._persons.find_by_document(employee_document)
        if not employee or employee.role != "EMPLOYEE":
            raise ValueError(f"employee {employee_document} not found")
        if not items:
            raise ValueError("invoice must have at least one item")

        invoice = Invoice(
            client_document=client_document,
            employee_document=employee_document,
            payment_method=payment_method,
        )
        for item in items:
            product = self._products.find_by_sku(item["sku"])
            if not product:
                raise ValueError(f"product {item['sku']} not found")
            quantity = int(item["quantity"])
            product.discount_stock(quantity)
            self._products.update_stock(product.sku, product.stock)
            invoice.add_detail(
                InvoiceDetail(
                    product_sku=product.sku,
                    product_name=product.name,
                    quantity=quantity,
                    unit_price=product.price,
                )
            )

        saved = self._invoices.save(invoice)

        for detail in saved.details:
            self._graph.register_purchase(client_document, detail.product_sku, detail.quantity)

        return saved

    def get(self, invoice_id: int) -> Optional[Invoice]:
        return self._invoices.find_by_id(invoice_id)

    def list(self, client_document: Optional[str] = None) -> List[Invoice]:
        return self._invoices.find_all(client_document=client_document)
