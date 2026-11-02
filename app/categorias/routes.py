
from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models.categoria import Categoria


categorias_bp = Blueprint(
    "categorias",
    __name__,
    url_prefix="/categorias"
)


def administrador_requerido(funcion):
    @wraps(funcion)
    @login_required
    def decorada(*args, **kwargs):
        if current_user.rol != "admin":
            abort(403)
        return funcion(*args, **kwargs)
    return decorada


@categorias_bp.route("/")
@administrador_requerido
def listar():
    categorias = db.session.scalars(
        db.select(Categoria).order_by(Categoria.id.desc())
    ).all()

    return render_template(
        "categorias/listar.html",
        categorias=categorias
    )


@categorias_bp.route("/nuevo", methods=["GET", "POST"])
@administrador_requerido
def nuevo():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        if not nombre:
            flash("El nombre de la categoría es obligatorio.", "danger")
        else:
            existente = db.session.scalar(
                db.select(Categoria).filter_by(nombre=nombre)
            )

            if existente:
                flash("Ya existe una categoría con ese nombre.", "danger")
            else:
                categoria = Categoria(
                    nombre=nombre,
                    descripcion=descripcion,
                    estado=True
                )

                db.session.add(categoria)
                db.session.commit()

                flash("Categoría registrada correctamente.", "success")
                return redirect(url_for("categorias.listar"))

    return render_template("categorias/nuevo.html")


@categorias_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@administrador_requerido
def editar(id):
    categoria = db.get_or_404(Categoria, id)

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        estado = request.form.get("estado") == "1"

        if not nombre:
            flash("El nombre de la categoría es obligatorio.", "danger")
        else:
            existente = db.session.scalar(
                db.select(Categoria).filter_by(nombre=nombre)
            )

            if existente and existente.id != categoria.id:
                flash("Ya existe otra categoría con ese nombre.", "danger")
            else:
                categoria.nombre = nombre
                categoria.descripcion = descripcion
                categoria.estado = estado

                db.session.commit()

                flash("Categoría actualizada correctamente.", "success")
                return redirect(url_for("categorias.listar"))

    return render_template(
        "categorias/editar.html",
        categoria=categoria
    )


@categorias_bp.route("/eliminar/<int:id>", methods=["POST"])
@administrador_requerido
def eliminar(id):
    categoria = db.get_or_404(Categoria, id)

    if categoria.anuncios:
        flash(
            "No se puede eliminar esta categoría porque tiene anuncios asociados.",
            "warning"
        )
    else:
        db.session.delete(categoria)
        db.session.commit()
        flash("Categoría eliminada correctamente.", "success")

    return redirect(url_for("categorias.listar"))
