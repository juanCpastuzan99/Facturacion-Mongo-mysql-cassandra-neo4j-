from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..container import Container

invoice_bp = Blueprint("invoices", __name__)


def _services():
    c = Container.instance()
    return c.invoice_service, c.person_service, c.product_service


@invoice_bp.route("/")
def index():
    invoice_svc, person_svc, _ = _services()
    client = request.args.get("client") or None
    invoices = invoice_svc.list(client_document=client)
    persons_map = {p.document: p.full_name for p in person_svc.list()}
    return render_template(
        "invoices/index.html",
        invoices=invoices,
        client=client,
        persons_map=persons_map,
    )


@invoice_bp.route("/<int:invoice_id>")
def detail(invoice_id):
    invoice_svc, person_svc, _ = _services()
    invoice = invoice_svc.get(invoice_id)
    if not invoice:
        flash("Factura no encontrada.", "warning")
        return redirect(url_for("invoices.index"))
    client = person_svc.get(invoice.client_document)
    employee = person_svc.get(invoice.employee_document)
    return render_template(
        "invoices/detail.html", invoice=invoice, client=client, employee=employee
    )


@invoice_bp.route("/new", methods=["GET", "POST"])
def create():
    invoice_svc, person_svc, product_svc = _services()
    clients = person_svc.list(role="CLIENT")
    employees = person_svc.list(role="EMPLOYEE")
    products = product_svc.list()

    if request.method == "POST":
        try:
            skus = request.form.getlist("sku")
            qtys = request.form.getlist("quantity")
            items = [
                {"sku": sku, "quantity": int(qty)}
                for sku, qty in zip(skus, qtys)
                if sku and int(qty or 0) > 0
            ]
            invoice = invoice_svc.create(
                client_document=request.form["client_document"],
                employee_document=request.form["employee_document"],
                payment_method=request.form["payment_method"],
                items=items,
            )
            flash(f"Factura #{invoice.id} creada por ${invoice.total:,.2f}.", "success")
            return redirect(url_for("invoices.detail", invoice_id=invoice.id))
        except (ValueError, KeyError) as exc:
            flash(str(exc), "danger")

    return render_template(
        "invoices/form.html", clients=clients, employees=employees, products=products
    )
