from flask_smorest import Blueprint, abort
from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from extensions import db
from models.usuario import Usuario
from models.paciente import Paciente
from models.profissional import Profissional
from utils.security import hash_password, verify_password
from utils.rbac import roles_required

blp = Blueprint("auth", __name__, url_prefix="/auth", description="Autenticação")

@blp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    senha = data.get("senha")
    if not email or not senha:
        abort(400, message="Informe email e senha")

    user = Usuario.query.filter_by(email=email, ativo=True).first()
    if not user or not verify_password(senha, user.senha_hash):
        abort(401, message="Credenciais inválidas")

    claims = {
        "role": user.role,
        "email": user.email,
        "paciente_id": user.paciente_id,
        "profissional_id": user.profissional_id,
    }
    # identity deve ser string
    token = create_access_token(identity=str(user.id), additional_claims=claims)
    return {"access_token": token}

@blp.route("/register", methods=["POST"])
@jwt_required()
@roles_required("admin")
def registrar_usuario():
    data = request.get_json() or {}
    email = data.get("email")
    senha = data.get("senha")
    role = data.get("role")  # 'paciente' | 'profissional' | 'admin'
    paciente_id = data.get("paciente_id")
    profissional_id = data.get("profissional_id")

    if not email or not senha or role not in ("paciente", "profissional", "admin"):
        abort(400, message="Campos obrigatórios: email, senha, role")

    if Usuario.query.filter_by(email=email).first():
        abort(409, message="Email já cadastrado")

    if role == "paciente":
        if not paciente_id:
            abort(400, message="Informe paciente_id para role 'paciente'")
        if not Paciente.query.get(paciente_id):
            abort(400, message="Paciente inválido")
        profissional_id = None  # coerência

    if role == "profissional":
        if not profissional_id:
            abort(400, message="Informe profissional_id para role 'profissional'")
        if not Profissional.query.get(profissional_id):
            abort(400, message="Profissional inválido")
        paciente_id = None  # coerência

    user = Usuario()  # Pylance-friendly (sem kwargs)
    user.email = email
    user.senha_hash = hash_password(senha)
    user.role = role
    user.paciente_id = paciente_id
    user.profissional_id = profissional_id

    db.session.add(user)
    db.session.commit()
    return {"id": user.id, "email": user.email, "role": user.role}, 201

@blp.route("/me", methods=["GET"])
@jwt_required()
def me():
    claims = get_jwt()
    return {
        "identity": get_jwt_identity(),          # string
        "role": claims.get("role"),
        "email": claims.get("email"),
        "paciente_id": claims.get("paciente_id"),
        "profissional_id": claims.get("profissional_id"),
    }
