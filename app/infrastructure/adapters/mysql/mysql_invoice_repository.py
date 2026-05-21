from typing import List, Optional

from ....domain.entities.invoice import Invoice
from ....domain.entities.invoice_detail import InvoiceDetail
from ....domain.ports.invoice_repository import InvoiceRepository
from .mysql_connection import MySQLConnection


class MySQLInvoiceRepository(InvoiceRepository):
    """Adaptador MySQL para factura y detalle_factura.

    Maneja transaccionalmente la inserción del encabezado y sus líneas.
    """

    def save(self, invoice: Invoice) -> Invoice:
        conn = MySQLConnection.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO factura
                  (client_document, employee_document, payment_method,
                   subtotal, tax_rate, tax, total, created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    invoice.client_document,
                    invoice.employee_document,
                    invoice.payment_method,
                    invoice.subtotal,
                    invoice.tax_rate,
                    invoice.tax,
                    invoice.total,
                    invoice.created_at,
                ),
            )
            invoice.id = cur.lastrowid

            cur.executemany(
                """
                INSERT INTO detalle_factura
                  (invoice_id, product_sku, product_name, quantity, unit_price, line_total)
                VALUES (%s,%s,%s,%s,%s,%s)
                """,
                [
                    (
                        invoice.id,
                        d.product_sku,
                        d.product_name,
                        d.quantity,
                        d.unit_price,
                        d.line_total,
                    )
                    for d in invoice.details
                ],
            )
            conn.commit()
            return invoice
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def find_by_id(self, invoice_id: int) -> Optional[Invoice]:
        conn = MySQLConnection.get_connection()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM factura WHERE id = %s", (invoice_id,))
            row = cur.fetchone()
            if not row:
                return None
            cur.execute(
                "SELECT * FROM detalle_factura WHERE invoice_id = %s ORDER BY id",
                (invoice_id,),
            )
            details = [self._row_to_detail(r) for r in cur.fetchall()]
            return self._row_to_invoice(row, details)
        finally:
            conn.close()

    def find_all(self, client_document: Optional[str] = None) -> List[Invoice]:
        conn = MySQLConnection.get_connection()
        try:
            cur = conn.cursor(dictionary=True)
            if client_document:
                cur.execute(
                    "SELECT * FROM factura WHERE client_document = %s ORDER BY id DESC",
                    (client_document,),
                )
            else:
                cur.execute("SELECT * FROM factura ORDER BY id DESC")
            rows = cur.fetchall()
            invoices: List[Invoice] = []
            for row in rows:
                cur.execute(
                    "SELECT * FROM detalle_factura WHERE invoice_id = %s ORDER BY id",
                    (row["id"],),
                )
                details = [self._row_to_detail(r) for r in cur.fetchall()]
                invoices.append(self._row_to_invoice(row, details))
            return invoices
        finally:
            conn.close()

    def find_purchased_skus_by_client(self, client_document: str) -> List[str]:
        conn = MySQLConnection.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT DISTINCT df.product_sku
                FROM factura f
                JOIN detalle_factura df ON df.invoice_id = f.id
                WHERE f.client_document = %s
                """,
                (client_document,),
            )
            return [row[0] for row in cur.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def _row_to_invoice(row: dict, details: List[InvoiceDetail]) -> Invoice:
        invoice = Invoice(
            id=row["id"],
            client_document=row["client_document"],
            employee_document=row["employee_document"],
            payment_method=row["payment_method"],
            tax_rate=float(row["tax_rate"]),
            created_at=row["created_at"],
            details=details,
        )
        for d in details:
            d.invoice_id = invoice.id
        return invoice

    @staticmethod
    def _row_to_detail(row: dict) -> InvoiceDetail:
        return InvoiceDetail(
            id=row["id"],
            invoice_id=row["invoice_id"],
            product_sku=row["product_sku"],
            product_name=row["product_name"],
            quantity=int(row["quantity"]),
            unit_price=float(row["unit_price"]),
        )
