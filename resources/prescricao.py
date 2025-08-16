from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db
from models.prescricao import Prescricao
from models.paciente import Paciente
from schemas.prescricao import PrescricaoIn, PrescricaoOut

blp = Blueprint("prescricoes", __name__, url_prefix="/prescricoes", description="Prescrições")

@blp.route("", methods=["GET"])
@jwt_required()
@blp.response(200, PrescricaoOut(many=True))
def listar():
    claims = get_jwt()
    role = claims.get("role")
    paciente_id_claim = claims.get("paciente_id")

    from flask import request
    paciente_id_qs = request.args.get("paciente_id", type=int)

    q = Prescricao.query

    if role == "paciente":
        q = q.filter(Prescricao.paciente_id == paciente_id_claim)
    elif role == "profissional":
        if not paciente_id_qs:
            abort(400, message="Informe paciente_id para listar as prescrições")
        q = q.filter(Prescricao.paciente_id == paciente_id_qs)
    if paciente_id_qs and role == "admin":
        q = q.filter(Prescricao.paciente_id == paciente_id_qs)

    return q.order_by(Prescricao.data.desc(), Prescricao.id.desc()).all()

@blp.route("", methods=["POST"])
@jwt_required()
@blp.arguments(PrescricaoIn)
@blp.response(201, PrescricaoOut)
def criar(payload):
    claims = get_jwt()
    role = claims.get("role")
    prof_id_token = claims.get("profissional_id")

    if not Paciente.query.get(payload["paciente_id"]):
        abort(400, message="Paciente inválido")

    pr = Prescricao()
    pr.paciente_id = payload["paciente_id"]
    pr.data = payload["data"]
    pr.texto = payload["texto"]

    if role == "profissional":
        if not prof_id_token:
            abort(403, message="Token de profissional inválido")
        pr.profissional_id = prof_id_token
    elif role == "admin":
        from flask import request
        prof_id_qs = request.args.get("profissional_id", type=int)
        if not prof_id_qs:
            abort(400, message="Admin deve informar profissional_id na query string")
        pr.profissional_id = prof_id_qs
    else:
        abort(403, message="Somente profissional ou admin podem emitir prescrição")

    db.session.add(pr)
    db.session.commit()
    return pr

@blp.route("/<int:pid>", methods=["GET"])
@jwt_required()
@blp.response(200, PrescricaoOut)
def obter(pid: int):
    claims = get_jwt()
    role = claims.get("role")
    paciente_id_claim = claims.get("paciente_id")

    pr = Prescricao.query.get(pid)
    if not pr:
        abort(404, message="Prescrição não encontrada")

    if role == "paciente" and pr.paciente_id != paciente_id_claim:
        abort(403, message="Acesso negado")
    return pr
