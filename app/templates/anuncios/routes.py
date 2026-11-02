
from functools import wraps
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models.anuncio import Anuncio
from app.models.categoria import Categoria
from app.models.usuario import Usuario


anuncios_bp = Blueprint(
    "anuncios",
    __name__,
    url_prefix="/anuncios"
)


def administrador_requerido(funcion):
    @wraps(funcion)
    @login_required
    def decorada(*args, **kwargs):
        if current_user.rol != "admin":
            abort(403)
        return funcion(*args, **kwargs)
    return decorada


def obtener_fecha_expiracion(valor):
    if not valor:
        return None

    try:
        return datetime.fromisoformat(valor)
    except ValueError:
        return False


@anuncios_bp.route("/")
@administrador_requerido
def listar():
    anuncios = db.session.scalars(
        db.select(Anuncio).order_by(Anuncio.fecha_publicacion.desc())
    ).all()

    return render_template(
        "anuncios/listar.html",
        anuncios=anuncios
    )


@anuncios_bp.route("/nuevo", methods=["GET", "POST"])
@administrador_requerido
def nuevo():
    categorias = db.session.scalars(
        db.select(Categoria)
        .filter_by(estado=True)
        .order_by(Categoria.nombre)
    ).all()

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        contenido = request.form.get("contenido", "").strip()
        imagen = request.form.get("imagen", "").strip()
        categoria_id = request.form.get("categoria_id", type=int)
        estado = request.form.get("estado", "borrador")
        fecha_expiracion = obtener_fecha_expiracion(
            request.form.get("fecha_expiracion", "")
        )

        categoria = db.session.get(Categoria, categoria_id) if categoria_id else None

        if not titulo or not contenido:
            flash("El título y el contenido son obligatorios.", "danger")
        elif not categoria or not categoria.estado:
            flash("Selecciona una categoría activa.", "danger")
        elif estado not in ["borrador", "publicado"]:
            flash("El estado seleccionado no es válido.", "danger")
        elif fecha_expiracion is False:
            flash("La fecha de expiración no es válida.", "danger")
        else:
            anuncio = Anuncio(
                titulo=titulo,
                contenido=contenido,
                imagen=imagen or None,
                estado=estado,
                usuario_id=current_user.id,
                categoria_id=categoria.id,
                fecha_expiracion=fecha_expiracion
            )

            db.session.add(anuncio)
            db.session.commit()

            flash("Anuncio registrado correctamente.", "success")
            return redirect(url_for("anuncios.listar"))

    return render_template(
        "anuncios/nuevo.html",
        categorias=categorias
    )


@anuncios_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@administrador_requerido
def editar(id):
    anuncio = db.get_or_404(Anuncio, id)

    categorias = db.session.scalars(
        db.select(Categoria)
        .filter(
            (Categoria.estado == True) |
            (Categoria.id == anuncio.categoria_id)
        )
        .order_by(Categoria.nombre)
    ).all()

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        contenido = request.form.get("contenido", "").strip()
        imagen = request.form.get("imagen", "").strip()
        categoria_id = request.form.get("categoria_id", type=int)
        estado = request.form.get("estado", "borrador")
        fecha_expiracion = obtener_fecha_expiracion(
            request.form.get("fecha_expiracion", "")
        )

        categoria = db.session.get(Categoria, categoria_id) if categoria_id else None

        if not titulo or not contenido:
            flash("El título y el contenido son obligatorios.", "danger")
        elif not categoria:
            flash("Selecciona una categoría válida.", "danger")
        elif estado not in ["borrador", "publicado"]:
            flash("El estado seleccionado no es válido.", "danger")
        elif fecha_expiracion is False:
            flash("La fecha de expiración no es válida.", "danger")
        else:
            anuncio.titulo = titulo
            anuncio.contenido = contenido
            anuncio.imagen = imagen or None
            anuncio.categoria_id = categoria.id
            anuncio.estado = estado
            anuncio.fecha_expiracion = fecha_expiracion

            db.session.commit()

            flash("Anuncio actualizado correctamente.", "success")
            return redirect(url_for("anuncios.listar"))

    return render_template(
        "anuncios/editar.html",
        anuncio=anuncio,
        categorias=categorias
    )


@anuncios_bp.route("/eliminar/<int:id>", methods=["POST"])
@administrador_requerido
def eliminar(id):
    anuncio = db.get_or_404(Anuncio, id)

    db.session.delete(anuncio)
    db.session.commit()

    flash("Anuncio eliminado correctamente.", "success")
    return redirect(url_for("anuncios.listar"))
