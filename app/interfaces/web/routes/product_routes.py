from flask import Blueprint, flash, redirect, render_template, request, url_for

from ....domain.entities.product import Product
from ..container import Container

product_bp = Blueprint("products", __name__)


def _service():
    return Container.instance().product_service


@product_bp.route("/")
def index():
    category = request.args.get("category") or None
    products = _service().list(category=category)
    return render_template("products/index.html", products=products, category=category)


@product_bp.route("/new", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        try:
            product = _build_from_form(request.form)
            _service().create(product)
            flash(f"Producto {product.name} creado.", "success")
            return redirect(url_for("products.index"))
        except (ValueError, KeyError) as exc:
            flash(str(exc), "danger")
            return render_template("products/form.html", product=request.form, mode="create")
    return render_template("products/form.html", product={}, mode="create")


@product_bp.route("/<sku>/edit", methods=["GET", "POST"])
def edit(sku):
    svc = _service()
    product = svc.get(sku)
    if not product:
        flash("Producto no encontrado.", "warning")
        return redirect(url_for("products.index"))
    if request.method == "POST":
        try:
            updated = _build_from_form(request.form, default_sku=sku)
            svc.update(updated)
            flash("Producto actualizado.", "success")
            return redirect(url_for("products.index"))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template("products/form.html", product=product, mode="edit")


@product_bp.route("/<sku>/delete", methods=["POST"])
def delete(sku):
    _service().delete(sku)
    flash("Producto eliminado.", "info")
    return redirect(url_for("products.index"))


def _build_from_form(form, default_sku: str | None = None) -> Product:
    tags_raw = form.get("tags", "")
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
    return Product(
        sku=form.get("sku") or default_sku,
        name=form["name"].strip(),
        description=form.get("description", "").strip(),
        category=form["category"].strip(),
        price=float(form["price"]),
        stock=int(form["stock"]),
        brand=form.get("brand", "").strip(),
        tags=tags,
        image_url=form.get("image_url", "").strip() or None,
    )
