from flask_smorest import Blueprint, abort
from flask import request
from extensions import db
from models.profissional import Profissional
from schemas.profissional import ProfissionalIn, ProfissionalOut
from flask_jwt_extended import jwt_required
from utils.rbac import roles_required

blp = Blueprint("profissionais", __name__, url_prefix="/profissionais", description="Profissionais")

@blp.route("", methods=["GET"])
@jwt_required()
@blp.response(200, ProfissionalOut(many=True))
def listar():
    return Profissional.query.order_by(Profissional.id.desc()).all()

@blp.route("", methods=["POST"])
@jwt_required()
@roles_required("admin")
@blp.arguments(ProfissionalIn)
@blp.response(201, ProfissionalOut)
def criar(payload):
    email = payload.get("email")
    if email and Profissional.query.filter_by(email=email).first():
        abort(409, message="Email já cadastrado")
    p = Profissional(**payload)
    db.session.add(p)
    db.session.commit()
    return p

@blp.route("/<int:prof_id>", methods=["GET"])
@blp.response(200, ProfissionalOut)
def obter(prof_id):
    p = Profissional.query.get(prof_id)
    if not p:
        abort(404, message="Profissional não encontrado")
    return p

@blp.route("/<int:prof_id>", methods=["PUT"])
@jwt_required()
@roles_required("admin")
@blp.arguments(ProfissionalIn)
@blp.response(200, ProfissionalOut)
def atualizar(payload, prof_id):
    p = Profissional.query.get(prof_id)
    if not p:
        abort(404, message="Profissional não encontrado")
    if payload.get("email"):
        existe = Profissional.query.filter(
            Profissional.email == payload["email"],
            Profissional.id != prof_id
        ).first()
        if existe:
            abort(409, message="Email já cadastrado para outro profissional")
    for k, v in payload.items():
        setattr(p, k, v)
    db.session.commit()
    return p

@blp.route("/<int:prof_id>", methods=["DELETE"])
@jwt_required()
@roles_required("admin")
@blp.response(204)
def deletar(prof_id):
    p = Profissional.query.get(prof_id)
    if not p:
        abort(404, message="Profissional não encontrado")
    db.session.delete(p)
    db.session.commit()
    return ""
