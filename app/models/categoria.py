from datetime import datetime, timezone
from app.extensions import db


class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    descripcion = db.Column(db.Text, nullable=True)

    estado = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    fecha_creacion = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    anuncios = db.relationship(
        "Anuncio",
        back_populates="categoria",
        lazy=True
    )

    def __repr__(self):
        return f"<Categoria {self.nombre}>"