from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db
from models.internacao import Internacao
from models.paciente import Paciente
from models.profissional import Profissional
from schemas.internacao import (
    InternacaoIn, InternacaoOut, InternacaoAltaIn, InternacaoUpdateIn
)

blp = Blueprint("internacoes", __name__, url_prefix="/internacoes", description="Internações (RF011)")

@blp.route("", methods=["GET"])
@jwt_required()
@blp.response(200, InternacaoOut(many=True))
def listar():
    claims = get_jwt()
    role = claims.get("role")
    paciente_id_claim = claims.get("paciente_id")
    prof_id_claim = claims.get("profissional_id")

    from flask import request
    paciente_id_qs = request.args.get("paciente_id", type=int)
    status_qs = request.args.get("status")  # admitido|alta (opcional)

    q = Internacao.query
    if role == "paciente":
        q = q.filter(Internacao.paciente_id == paciente_id_claim)
    elif role == "profissional":
        # Para evitar dump geral, exija filtro por paciente_id
        if not paciente_id_qs:
            abort(400, message="Informe paciente_id para listar internações")
        q = q.filter(Internacao.paciente_id == paciente_id_qs)
    else:
        # admin pode filtrar por paciente_id se quiser
        if paciente_id_qs:
            q = q.filter(Internacao.paciente_id == paciente_id_qs)

    if status_qs in ("admitido", "alta"):
        q = q.filter(Internacao.status == status_qs)

    return q.order_by(Internacao.id.desc()).all()

@blp.route("", methods=["POST"])
@jwt_required()
@blp.arguments(InternacaoIn)
@blp.response(201, InternacaoOut)
def admitir(payload):
    """Admite um paciente. Profissional usa seu próprio ID; admin informa ?profissional_id= na query."""
    claims = get_jwt()
    role = claims.get("role")
    prof_id_token = claims.get("profissional_id")

    if not Paciente.query.get(payload["paciente_id"]):
        abort(400, message="Paciente inválido")

    if role == "profissional":
        profissional_id = prof_id_token
        if not profissional_id:
            abort(403, message="Token de profissional inválido")
    elif role == "admin":
        from flask import request
        profissional_id = request.args.get("profissional_id", type=int)
        if not profissional_id or not Profissional.query.get(profissional_id):
            abort(400, message="Admin deve informar um profissional_id válido")
    else:
        abort(403, message="Apenas profissional ou admin podem admitir")

    i = Internacao()
    i.paciente_id = payload["paciente_id"]
    i.profissional_id = profissional_id
    i.data_entrada = payload["data_entrada"]
    i.leito = payload.get("leito")
    i.diagnostico = payload.get("diagnostico")
    i.status = "admitido"

    db.session.add(i)
    db.session.commit()
    return i

@blp.route("/<int:iid>", methods=["GET"])
@jwt_required()
@blp.response(200, InternacaoOut)
def obter(iid: int):
    claims = get_jwt()
    role = claims.get("role")
    paciente_id_claim = claims.get("paciente_id")
    prof_id_claim = claims.get("profissional_id")

    i = Internacao.query.get(iid)
    if not i:
        abort(404, message="Internação não encontrada")

    if role == "paciente" and i.paciente_id != paciente_id_claim:
        abort(403, message="Acesso negado")
    if role == "profissional" and i.profissional_id != prof_id_claim:
        abort(403, message="Acesso negado")

    return i

@blp.route("/<int:iid>", methods=["PATCH"])
@jwt_required()
@blp.arguments(InternacaoUpdateIn)
@blp.response(200, InternacaoOut)
def atualizar(payload, iid: int):
    """Atualiza leito/diagnóstico. Apenas profissional responsável ou admin."""
    claims = get_jwt()
    role = claims.get("role")
    prof_id_claim = claims.get("profissional_id")

    i = Internacao.query.get(iid)
    if not i:
        abort(404, message="Internação não encontrada")

    if role == "profissional" and i.profissional_id != prof_id_claim:
        abort(403, message="Acesso negado")

    if "leito" in payload:
        i.leito = payload["leito"]
    if "diagnostico" in payload:
        i.diagnostico = payload["diagnostico"]

    db.session.commit()
    return i

@blp.route("/<int:iid>/alta", methods=["PATCH"])
@jwt_required()
@blp.arguments(InternacaoAltaIn)
@blp.response(200, InternacaoOut)
def alta(payload, iid: int):
    """Dá alta. Apenas profissional responsável ou admin."""
    claims = get_jwt()
    role = claims.get("role")
    prof_id_claim = claims.get("profissional_id")

    i = Internacao.query.get(iid)
    if not i:
        abort(404, message="Internação não encontrada")

    if role == "profissional" and i.profissional_id != prof_id_claim:
        abort(403, message="Acesso negado")

    if i.status == "alta":
        return i  # idempotente

    data_alta = payload["data_alta"]
    if data_alta < i.data_entrada:
        abort(400, message="data_alta não pode ser anterior à data_entrada")

    i.status = "alta"
    i.data_alta = data_alta

    db.session.commit()
    return i
