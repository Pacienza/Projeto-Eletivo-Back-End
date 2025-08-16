from flask_smorest import Blueprint, abort
from flask import request
from extensions import db
from models.paciente import Paciente
from schemas.paciente import PacienteIn, PacienteOut

blp = Blueprint(
    "pacientes", __name__, url_prefix="/pacientes", description="Pacientes"
)

@blp.route("", methods=["GET"])
@blp.response(200, PacienteOut(many=True))
def listar_pacientes():
    return Paciente.query.order_by(Paciente.id.desc()).all()

@blp.route("", methods=["POST"])
@blp.arguments(PacienteIn)
@blp.response(201, PacienteOut)
def criar_paciente(payload):
    # validação simples de email único
    email = payload.get("email")
    if email:
        if Paciente.query.filter_by(email=email).first():
            abort(409, message="Email já cadastrado")

    paciente = Paciente(**payload)
    db.session.add(paciente)
    db.session.commit()
    return paciente

@blp.route("/<int:paciente_id>", methods=["GET"])
@blp.response(200, PacienteOut)
def obter_paciente(paciente_id: int):
    p = Paciente.query.get(paciente_id)
    if not p:
        abort(404, message="Paciente não encontrado")
    return p

@blp.route("/<int:paciente_id>", methods=["PUT"])
@blp.arguments(PacienteIn)
@blp.response(200, PacienteOut)
def atualizar_paciente(payload, paciente_id: int):
    p = Paciente.query.get(paciente_id)
    if not p:
        abort(404, message="Paciente não encontrado")

    if "email" in payload and payload["email"]:
        existe = Paciente.query.filter(
            Paciente.email == payload["email"],
            Paciente.id != paciente_id
        ).first()
        if existe:
            abort(409, message="Email já cadastrado para outro paciente")

    for k, v in payload.items():
        setattr(p, k, v)
    db.session.commit()
    return p

@blp.route("/<int:paciente_id>", methods=["DELETE"])
@blp.response(204)
def deletar_paciente(paciente_id: int):
    p = Paciente.query.get(paciente_id)
    if not p:
        abort(404, message="Paciente não encontrado")
    db.session.delete(p)
    db.session.commit()
    return ""
