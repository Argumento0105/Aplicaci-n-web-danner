from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models.usuario import Usuario


usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


def administrador_requerido(funcion):
    @wraps(funcion)
    @login_required
    def decorada(*args, **kwargs):
        if current_user.rol != "admin":
            abort(403)
        return funcion(*args, **kwargs)
    return decorada


@usuarios_bp.route("/")
@administrador_requerido
def listar():
    usuarios = db.session.scalars(
        db.select(Usuario).order_by(Usuario.id.desc())
    ).all()

    return render_template("usuarios/listar.html", usuarios=usuarios)


@usuarios_bp.route("/nuevo", methods=["GET", "POST"])
@administrador_requerido
def nuevo():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        apellido = request.form.get("apellido", "").strip()
        correo = request.form.get("correo", "").strip().lower()
        password = request.form.get("password", "")
        rol = request.form.get("rol", "usuario")

        if not nombre or not apellido or not correo or not password:
            flash("Completa todos los campos obligatorios.", "danger")
            return render_template("usuarios/nuevo.html")

        if len(password) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "danger")
            return render_template("usuarios/nuevo.html")

        if rol not in ["admin", "usuario"]:
            flash("El rol seleccionado no es válido.", "danger")
            return render_template("usuarios/nuevo.html")

        existente = db.session.scalar(
            db.select(Usuario).filter_by(correo=correo)
        )

        if existente:
            flash("Ya existe un usuario con ese correo.", "danger")
            return render_template("usuarios/nuevo.html")

        usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            rol=rol,
            estado=True
        )
        usuario.establecer_password(password)

        db.session.add(usuario)
        db.session.commit()

        flash("Usuario registrado correctamente.", "success")
        return redirect(url_for("usuarios.listar"))

    return render_template("usuarios/nuevo.html")


@usuarios_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@administrador_requerido
def editar(id):
    usuario = db.get_or_404(Usuario, id)

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        apellido = request.form.get("apellido", "").strip()
        correo = request.form.get("correo", "").strip().lower()
        password = request.form.get("password", "")
        rol = request.form.get("rol", "usuario")
        estado = request.form.get("estado") == "1"

        if not nombre or not apellido or not correo:
            flash("Completa los campos obligatorios.", "danger")
            return render_template("usuarios/editar.html", usuario=usuario)

        if rol not in ["admin", "usuario"]:
            flash("El rol seleccionado no es válido.", "danger")
            return render_template("usuarios/editar.html", usuario=usuario)

        existente = db.session.scalar(
            db.select(Usuario).filter_by(correo=correo)
        )

        if existente and existente.id != usuario.id:
            flash("Ese correo ya está registrado por otro usuario.", "danger")
            return render_template("usuarios/editar.html", usuario=usuario)

        if password and len(password) < 8:
            flash("La nueva contraseña debe tener al menos 8 caracteres.", "danger")
            return render_template("usuarios/editar.html", usuario=usuario)

        usuario.nombre = nombre
        usuario.apellido = apellido
        usuario.correo = correo
        usuario.rol = rol
        usuario.estado = estado

        if password:
            usuario.establecer_password(password)

        db.session.commit()

        flash("Usuario actualizado correctamente.", "success")
        return redirect(url_for("usuarios.listar"))

    return render_template("usuarios/editar.html", usuario=usuario)


@usuarios_bp.route("/eliminar/<int:id>", methods=["POST"])
@administrador_requerido
def eliminar(id):
    usuario = db.get_or_404(Usuario, id)

    if usuario.id == current_user.id:
        flash("No puedes eliminar tu propia cuenta de administrador.", "warning")
        return redirect(url_for("usuarios.listar"))

    if usuario.anuncios:
        flash(
            "No se puede eliminar este usuario porque tiene anuncios registrados.",
            "warning"
        )
        return redirect(url_for("usuarios.listar"))

    db.session.delete(usuario)
    db.session.commit()

    flash("Usuario eliminado correctamente.", "success")
    return redirect(url_for("usuarios.listar"))