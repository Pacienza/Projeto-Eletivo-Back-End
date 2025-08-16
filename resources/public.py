from flask_smorest import Blueprint, abort
from flask import request
from extensions import db
from models.paciente import Paciente
from models.usuario import Usuario
from utils.security import hash_password

blp = Blueprint("public", __name__, url_prefix="/public", description="Rotas públicas")

@blp.route("/cadastro_paciente", methods=["POST"])
def cadastro_paciente():
    data = request.get_json() or {}
    nome = data.get("nome")
    email = data.get("email")
    senha = data.get("senha")
    data_nascimento = data.get("data_nascimento")  # dd/mm/aaaa opcional

    if not nome or not email or not senha:
        abort(400, message="Campos obrigatórios: nome, email, senha")

    # Paciente
    p = Paciente()
    p.nome = nome
    p.email = email
    # parse opcional da data
    if data_nascimento:
        from schemas.common import DateDDMMYYYY
        p.data_nascimento = DateDDMMYYYY()._deserialize(data_nascimento, "data_nascimento", None)

    # Usuario
    if Usuario.query.filter_by(email=email).first():
        abort(409, message="Email já cadastrado")
    u = Usuario()
    u.email = email
    u.senha_hash = hash_password(senha)
    u.role = "paciente"

    db.session.add(p)
    db.session.flush()  # pega p.id
    u.paciente_id = p.id
    db.session.add(u)
    db.session.commit()

    return {"paciente_id": p.id, "usuario_id": u.id}, 201
