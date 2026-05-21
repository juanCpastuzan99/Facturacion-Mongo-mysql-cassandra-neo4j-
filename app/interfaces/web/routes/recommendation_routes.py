from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..container import Container

recommendation_bp = Blueprint("recommendations", __name__)


@recommendation_bp.route("/", methods=["GET", "POST"])
def index():
    c = Container.instance()
    clients = c.person_service.list(role="CLIENT")
    recommendations = []
    selected = None
    client = None
    if request.method == "POST":
        selected = request.form.get("client_document")
        try:
            recommendations = c.recommendation_service.recommend(selected, limit=8)
            client = c.person_service.get(selected)
            if not recommendations:
                flash(
                    "No hay recomendaciones todavía. Registra algunas compras para "
                    "alimentar el grafo.",
                    "info",
                )
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("recommendations.index"))
    return render_template(
        "recommendations/index.html",
        clients=clients,
        recommendations=recommendations,
        selected=selected,
        client=client,
    )
