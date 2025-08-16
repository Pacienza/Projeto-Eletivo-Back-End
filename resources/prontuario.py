from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db
from models.prontuario import Prontuario
from models.paciente import Paciente
from schemas.prontuario import ProntuarioIn, ProntuarioOut

blp = Blueprint("prontuarios", __name__, url_prefix="/prontuarios", description="Prontuário clínico")

@blp.route("", methods=["GET"])
@jwt_required()
@blp.response(200, ProntuarioOut(many=True))
def listar():
    claims = get_jwt()
    role = claims.get("role")
    paciente_id_claim = claims.get("paciente_id")

    # Filtros opcionais
    from flask import request
    paciente_id_qs = request.args.get("paciente_id", type=int)

    q = Prontuario.query

    if role == "paciente":
        # paciente só enxerga os seus
        q = q.filter(Prontuario.paciente_id == paciente_id_claim)
    elif role == "profissional":
        # profissional vê históricos por paciente (RF009); exige paciente_id para evitar dump geral
        if not paciente_id_qs:
            abort(400, message="Informe paciente_id para listar o histórico")
        q = q.filter(Prontuario.paciente_id == paciente_id_qs)
    # admin pode ver tudo (ou filtrar por paciente_id se enviado)
    if paciente_id_qs and role == "admin":
        q = q.filter(Prontuario.paciente_id == paciente_id_qs)

    return q.order_by(Prontuario.data.desc(), Prontuario.id.desc()).all()

@blp.route("", methods=["POST"])
@jwt_required()
@blp.arguments(ProntuarioIn)
@blp.response(201, ProntuarioOut)
def criar(payload):
    claims = get_jwt()
    role = claims.get("role")
    prof_id_token = claims.get("profissional_id")

    pac = Paciente.query.get(payload["paciente_id"])
    if not pac:
        abort(400, message="Paciente inválido")

    p = Prontuario()
    p.paciente_id = payload["paciente_id"]
    p.data = payload["data"]
    p.resumo = payload["resumo"]
    p.anotacoes = payload.get("anotacoes")

    if role == "profissional":
        if not prof_id_token:
            abort(403, message="Token de profissional inválido")
        p.profissional_id = prof_id_token
    elif role == "admin":
        # admin pode opcionalmente informar profissional_id via query param (?profissional_id=)
        from flask import request
        prof_id_qs = request.args.get("profissional_id", type=int)
        if not prof_id_qs:
            abort(400, message="Admin deve informar profissional_id na query string")
        p.profissional_id = prof_id_qs
    else:
        abort(403, message="Somente profissional ou admin podem registrar prontuário")

    db.session.add(p)
    db.session.commit()
    return p

@blp.route("/<int:pid>", methods=["GET"])
@jwt_required()
@blp.response(200, ProntuarioOut)
def obter(pid: int):
    claims = get_jwt()
    role = claims.get("role")
    paciente_id_claim = claims.get("paciente_id")

    p = Prontuario.query.get(pid)
    if not p:
        abort(404, message="Registro não encontrado")

    if role == "paciente" and p.paciente_id != paciente_id_claim:
        abort(403, message="Acesso negado")
    # profissional pode ler histórico de um paciente (RF009)
    # admin tudo
    return p

@blp.route("/<int:pid>", methods=["PUT"])
@jwt_required()
@blp.arguments(ProntuarioIn)
@blp.response(200, ProntuarioOut)
def atualizar(payload, pid: int):
    claims = get_jwt()
    role = claims.get("role")
    prof_id_token = claims.get("profissional_id")

    p = Prontuario.query.get(pid)
    if not p:
        abort(404, message="Registro não encontrado")

    if role == "profissional":
        if p.profissional_id != prof_id_token:
            abort(403, message="Profissional só edita registros criados por ele")
    elif role != "admin":
        abort(403, message="Acesso negado")

    # atualiza campos
    p.paciente_id = payload["paciente_id"]
    p.data = payload["data"]
    p.resumo = payload["resumo"]
    p.anotacoes = payload.get("anotacoes")

    db.session.commit()
    return p
