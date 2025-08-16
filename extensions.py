# CÓDIGO / passa a usar MetaData com convenções de nome
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_smorest import Api
from flask_cors import CORS
from marshmallow import ValidationError

# adiciona esta convenção
NAMING_CONVENTION = {
    "ix":  "ix_%(table_name)s_%(column_0_name)s",
    "uq":  "uq_%(table_name)s_%(column_0_name)s",
    "ck":  "ck_%(table_name)s_%(constraint_name)s",
    "fk":  "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk":  "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=NAMING_CONVENTION)

db = SQLAlchemy(metadata=metadata)
migrate = Migrate()
jwt = JWTManager()
api = Api()
cors = CORS()
limiter = Limiter(key_func=get_remote_address, default_limits=["60 per minute"])

def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    api.init_app(app)
    cors.init_app(app)
    limiter.init_app(app)

    @app.errorhandler(ValidationError)
    def handle_ma_error(err):
        return {"message": "Dados inválidos", "errors": err.messages}, 400
