from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for

from ....domain.entities.person import Person
from ..container import Container

person_bp = Blueprint("persons", __name__)


def _service():
    return Container.instance().person_service


@person_bp.route("/")
def index():
    role = request.args.get("role") or None
    persons = _service().list(role=role)
    return render_template("persons/index.html", persons=persons, role=role)


@person_bp.route("/new", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        try:
            person = _build_from_form(request.form)
            _service().create(person)
            flash(f"Persona {person.full_name} creada exitosamente.", "success")
            return redirect(url_for("persons.index"))
        except (ValueError, KeyError) as exc:
            flash(str(exc), "danger")
            return render_template("persons/form.html", person=request.form, mode="create")
    return render_template("persons/form.html", person={}, mode="create")


@person_bp.route("/<document>/edit", methods=["GET", "POST"])
def edit(document):
    svc = _service()
    person = svc.get(document)
    if not person:
        flash("Persona no encontrada.", "warning")
        return redirect(url_for("persons.index"))
    if request.method == "POST":
        try:
            updated = _build_from_form(request.form, default_document=document)
            svc.update(updated)
            flash("Persona actualizada.", "success")
            return redirect(url_for("persons.index"))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template("persons/form.html", person=person, mode="edit")


@person_bp.route("/<document>/delete", methods=["POST"])
def delete(document):
    _service().delete(document)
    flash("Persona eliminada.", "info")
    return redirect(url_for("persons.index"))


def _build_from_form(form, default_document: str | None = None) -> Person:
    salary_raw = form.get("salary")
    return Person(
        document=form.get("document") or default_document,
        first_name=form["first_name"].strip(),
        last_name=form["last_name"].strip(),
        role=form["role"],
        email=form["email"].strip(),
        phone=form["phone"].strip(),
        birth_date=date.fromisoformat(form["birth_date"]),
        gender=form["gender"],
        stratum=int(form["stratum"]),
        neighborhood=form["neighborhood"].strip(),
        municipality=form["municipality"].strip(),
        department=form["department"].strip(),
        salary=float(salary_raw) if salary_raw else None,
    )
