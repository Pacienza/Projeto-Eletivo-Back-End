from flask import Flask
from config import DevConfig
from extensions import init_extensions, db
from models import *
import click


def create_app(config_object=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_object)
    init_extensions(app)

    # SQLite: ativa WAL em dev
    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):
        with app.app_context():
            db.session.execute(db.text("PRAGMA foreign_keys=ON;"))
            db.session.execute(db.text("PRAGMA journal_mode=WAL;"))
            db.session.commit()

    from resources.auth import blp as auth_blp
    from resources.paciente import blp as pac_blp
    from resources.profissional import blp as prof_blp
    from resources.agenda import blp as ag_blp
    from resources.consulta import blp as cons_blp
    from resources.prontuario import blp as pront_blp
    from resources.prescricao import blp as pres_blp
    from resources.internacao import blp as int_blp
    from resources.notificacao import blp as notif_blp
    from resources.teleconsulta import blp as tele_blp
    from resources.teleconsulta import blp as tele_blp
    from resources.public import blp as public_blp
    from resources.me import blp as me_blp
    from resources.relatorios import blp as rel_blp

    from extensions import api
    api.register_blueprint(auth_blp)
    api.register_blueprint(pac_blp)
    api.register_blueprint(prof_blp)
    api.register_blueprint(ag_blp)
    api.register_blueprint(cons_blp)
    api.register_blueprint(pront_blp)
    api.register_blueprint(pres_blp)
    api.register_blueprint(int_blp)
    api.register_blueprint(notif_blp)
    api.register_blueprint(tele_blp)
    api.register_blueprint(public_blp)
    api.register_blueprint(me_blp)
    api.register_blueprint(rel_blp)

    @app.cli.command("seed-admin")
    @click.option("--email", required=True)
    @click.option("--senha", required=True)
    def seed_admin(email, senha):
        """Cria um usuário admin básico."""
        from models.usuario import Usuario
        from utils.security import hash_password
        from extensions import db

        with app.app_context():
            if Usuario.query.filter_by(email=email).first():
                click.echo("Já existe usuário com este email.")
                return
            u = Usuario()
            u.email = email
            u.senha_hash = hash_password(senha)
            u.role = "admin"
            db.session.add(u)
            db.session.commit()
            click.echo(f"Admin criado: id={u.id}, email={u.email}")

    @app.get("/")
    def health():
        return {"status": "ok"}

    return app
