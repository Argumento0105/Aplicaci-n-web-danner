from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.extensions import db
from app.models.usuario import Usuario
from app.models.categoria import Categoria
from app.models.anuncio import Anuncio

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():

    anuncios = db.session.scalars(
        db.select(Anuncio)
        .filter_by(estado="publicado")
        .order_by(Anuncio.fecha_publicacion.desc())
    ).all()

    categorias = db.session.scalars(
        db.select(Categoria).filter_by(estado=True)
    ).all()

    return render_template(
        "main/index.html",
        anuncios=anuncios,
        categorias=categorias
    )


@main_bp.route("/dashboard")
@login_required
def dashboard():

    if current_user.rol != "admin":
        return render_template("main/acceso_denegado.html"), 403

    total_usuarios = db.session.scalar(
        db.select(db.func.count()).select_from(Usuario)
    )

    total_categorias = db.session.scalar(
        db.select(db.func.count()).select_from(Categoria)
    )

    total_anuncios = db.session.scalar(
        db.select(db.func.count()).select_from(Anuncio)
    )

    return render_template(
        "main/dashboard.html",
        total_usuarios=total_usuarios,
        total_categorias=total_categorias,
        total_anuncios=total_anuncios
    )