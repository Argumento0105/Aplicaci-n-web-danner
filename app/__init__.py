from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager, csrf
from app.categorias import categorias_bp
from app.anuncios import anuncios_bp


def create_app(config_class=Config):

    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.models import Usuario, Categoria, Anuncio
    from app.main import main_bp
    from app.auth import auth_bp
    from app.usuarios import usuarios_bp
    from app.anuncios import anuncios_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(anuncios_bp)

    return app