from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db
from models.agenda import Agenda
from models.profissional import Profissional
from schemas.agenda import AgendaIn, AgendaOut

blp = Blueprint("agendas", __name__, url_prefix="/agendas", description="Agendas (slots)")

@blp.route("", methods=["GET"])
@jwt_required()
@blp.response(200, AgendaOut(many=True))
def listar():
    return Agenda.query.order_by(Agenda.data.desc(), Agenda.hora.desc()).all()

@blp.route("", methods=["POST"])
@jwt_required()
@blp.arguments(AgendaIn)
@blp.response(201, AgendaOut)
def criar(payload):
    claims = get_jwt()  # <- com parênteses
    role = claims.get("role")
    prof_id_token = claims.get("profissional_id")

    # Profissional só cria slots na própria agenda
    if role == "profissional" and payload["profissional_id"] != prof_id_token:
        abort(403, message="Você só pode criar vagas para sua própria agenda")

    # Valida profissional
    prof = Profissional.query.get(payload["profissional_id"])
    if not prof:
        abort(400, message="Profissional inválido")

    # Criação Pylance-friendly
    ag = Agenda()
    ag.profissional_id = payload["profissional_id"]
    ag.data = payload["data"]
    ag.hora = payload["hora"]
    ag.disponivel = True

    db.session.add(ag)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(409, message="Slot já existe para esse profissional")
    return ag

@blp.route("/<int:agenda_id>/liberar", methods=["PATCH"])
@jwt_required()
@blp.response(200, AgendaOut)
def liberar(agenda_id):
    claims = get_jwt()
    role = claims.get("role")
    prof_id_token = claims.get("profissional_id")

    ag = Agenda.query.get(agenda_id)
    if not ag:
        abort(404, message="Agenda não encontrada")

    if role == "profissional" and ag.profissional_id != prof_id_token:
        abort(403, message="Você só pode alterar sua própria agenda")

    ag.disponivel = True
    db.session.commit()
    return ag

@blp.route("/<int:agenda_id>/bloquear", methods=["PATCH"])
@jwt_required()
@blp.response(200, AgendaOut)
def bloquear(agenda_id):
    claims = get_jwt()
    role = claims.get("role")
    prof_id_token = claims.get("profissional_id")

    ag = Agenda.query.get(agenda_id)
    if not ag:
        abort(404, message="Agenda não encontrada")

    if role == "profissional" and ag.profissional_id != prof_id_token:
        abort(403, message="Você só pode alterar sua própria agenda")

    ag.disponivel = False
    db.session.commit()
    return ag
