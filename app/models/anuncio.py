from datetime import datetime, timezone
from app.extensions import db


class Anuncio(db.Model):
    __tablename__ = "anuncios"

    id = db.Column(db.Integer, primary_key=True)

    titulo = db.Column(
        db.String(150),
        nullable=False
    )

    contenido = db.Column(
        db.Text,
        nullable=False
    )

    imagen = db.Column(
        db.String(255),
        nullable=True
    )

    fecha_publicacion = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    fecha_expiracion = db.Column(
        db.DateTime,
        nullable=True
    )

    estado = db.Column(
        db.String(20),
        nullable=False,
        default="borrador"
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    categoria_id = db.Column(
        db.Integer,
        db.ForeignKey("categorias.id"),
        nullable=False
    )

    usuario = db.relationship(
        "Usuario",
        back_populates="anuncios"
    )

    categoria = db.relationship(
        "Categoria",
        back_populates="anuncios"
    )

    def __repr__(self):
        return f"<Anuncio {self.titulo}>"