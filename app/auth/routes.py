from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.extensions import db
from app.models.usuario import Usuario
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


class LoginForm(FlaskForm):
    correo = StringField(
        "Correo electrónico",
        validators=[DataRequired(), Email()]
    )

    password = PasswordField(
        "Contraseña",
        validators=[DataRequired()]
    )

    submit = SubmitField("Iniciar sesión")


class RegistroForm(FlaskForm):
    nombre = StringField(
        "Nombre",
        validators=[DataRequired(), Length(max=100)]
    )

    apellido = StringField(
        "Apellido",
        validators=[DataRequired(), Length(max=100)]
    )

    correo = StringField(
        "Correo electrónico",
        validators=[DataRequired(), Email(), Length(max=120)]
    )

    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(), Length(min=8)]
    )

    submit = SubmitField("Registrarse")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()

    if form.validate_on_submit():

        correo = form.correo.data.strip().lower()

        usuario = db.session.scalar(
            db.select(Usuario).filter_by(correo=correo)
        )

        if usuario and usuario.verificar_password(form.password.data):

            if not usuario.estado:
                flash("Tu cuenta se encuentra desactivada.", "danger")
                return render_template("auth/login.html", form=form)

            login_user(usuario)

            flash("Bienvenido a ANUNCIA.", "success")

            next_page = request.args.get("next")

            if next_page and next_page.startswith("/") and not next_page.startswith("//"):
                return redirect(next_page)

            return redirect(url_for("main.dashboard"))

        flash("Correo electrónico o contraseña incorrectos.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():

    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegistroForm()

    if form.validate_on_submit():

        correo = form.correo.data.strip().lower()

        existente = db.session.scalar(
            db.select(Usuario).filter_by(correo=correo)
        )

        if existente:
            flash("Este correo electrónico ya está registrado.", "danger")
            return render_template("auth/registro.html", form=form)

        usuario = Usuario(
            nombre=form.nombre.data.strip(),
            apellido=form.apellido.data.strip(),
            correo=correo,
            rol="usuario",
            estado=True
        )

        usuario.establecer_password(form.password.data)

        db.session.add(usuario)
        db.session.commit()

        flash("Registro exitoso. Ya puedes iniciar sesión.", "success")

        return redirect(url_for("auth.login"))

    return render_template("auth/registro.html", form=form)


@auth_bp.route("/logout")
def logout():

    if current_user.is_authenticated:
        logout_user()
        flash("Has cerrado sesión correctamente.", "success")

    return redirect(url_for("main.index"))