from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db
from models.usuario import Usuario
from models.notificacao import Notificacao
from models.consulta import Consulta
from models.paciente import Paciente
from models.profissional import Profissional
from models.agenda import Agenda
from schemas.consulta import ConsultaIn, ConsultaOut

blp = Blueprint("consultas", __name__, url_prefix="/consultas", description="Consultas")

@blp.route("", methods=["GET"])
@jwt_required()
@blp.response(200, ConsultaOut(many=True))
def listar():
    return Consulta.query.order_by(Consulta.data.desc(), Consulta.hora.desc()).all()

@blp.route("", methods=["POST"])
@jwt_required()
@blp.arguments(ConsultaIn)
@blp.response(201, ConsultaOut)
def agendar(payload):
    claims = get_jwt()
    role = claims.get("role")
    pac_id_token = claims.get("paciente_id")
    prof_id_token = claims.get("profissional_id")

    # RBAC
    if role == "paciente" and payload["paciente_id"] != pac_id_token:
        abort(403, message="Paciente só pode agendar para si")
    if role == "profissional" and payload["profissional_id"] != prof_id_token:
        abort(403, message="Profissional só pode agendar na própria agenda")

    # valida existência (também para notificação)
    pac = Paciente.query.get(payload["paciente_id"])
    if not pac:
        abort(400, message="Paciente inválido")
    prof = Profissional.query.get(payload["profissional_id"])
    if not prof:
        abort(400, message="Profissional inválido")

    # exige slot disponível
    slot = Agenda.query.filter_by(
        profissional_id=payload["profissional_id"],
        data=payload["data"],
        hora=payload["hora"],
        disponivel=True
    ).first()
    if not slot:
        abort(409, message="Não há slot disponível na agenda para data/hora informadas")

    # cria consulta (Pylance ok)
    c = Consulta(**payload)
    c.status = "agendada"
    c.status_open = True
    db.session.add(c)

    # bloqueia slot
    slot.disponivel = False

    # Notificações (paciente e profissional, se tiverem usuário)
    u_paciente = Usuario.query.filter_by(paciente_id=pac.id, ativo=True).first()
    u_prof = Usuario.query.filter_by(profissional_id=prof.id, ativo=True).first()

    titulo_pac = "Consulta agendada"
    titulo_prof = "Nova consulta na sua agenda"
    mensagem = (
        f"Sua consulta em {payload['data'].strftime('%d/%m/%Y')} "
        f"às {payload['hora'].strftime('%H:%M')} foi agendada."
    )

    if u_paciente:
        n = Notificacao()
        n.usuario_id = u_paciente.id
        n.tipo = "consulta_agendada"
        n.titulo = titulo_pac
        n.mensagem = mensagem
        n.consulta_id = None
        db.session.add(n)

    if u_prof:
        n2 = Notificacao()
        n2.usuario_id = u_prof.id
        n2.tipo = "consulta_agendada"
        n2.titulo = titulo_prof
        n2.mensagem = mensagem
        n2.consulta_id = None
        db.session.add(n2)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        abort(409, message="Conflito: já existe consulta aberta nesse horário")

    return c

@blp.route("/<int:consulta_id>/cancelar", methods=["PATCH"])
@jwt_required()
@blp.response(200, ConsultaOut)
def cancelar(consulta_id):
    claims = get_jwt()
    role = claims.get("role")
    pac_id_token = claims.get("paciente_id")
    prof_id_token = claims.get("profissional_id")

    c = Consulta.query.get(consulta_id)
    if not c:
        abort(404, message="Consulta não encontrada")

    # RBAC
    if role == "paciente" and c.paciente_id != pac_id_token:
        abort(403, message="Paciente só pode cancelar a própria consulta")
    if role == "profissional" and c.profissional_id != prof_id_token:
        abort(403, message="Profissional só pode cancelar consultas próprias")

    if c.status == "cancelada":
        return c  # idempotente

    c.status = "cancelada"
    c.status_open = False

    # libera o slot
    slot = Agenda.query.filter_by(
        profissional_id=c.profissional_id, data=c.data, hora=c.hora
    ).first()
    if slot:
        slot.disponivel = True

    # Notificações de cancelamento
    u_paciente = Usuario.query.filter_by(paciente_id=c.paciente_id, ativo=True).first()
    u_prof = Usuario.query.filter_by(profissional_id=c.profissional_id, ativo=True).first()

    mensagem = (
        f"Sua consulta em {c.data.strftime('%d/%m/%Y')} "
        f"às {c.hora.strftime('%H:%M')} foi cancelada."
    )

    if u_paciente:
        n = Notificacao()
        n.usuario_id = u_paciente.id
        n.tipo = "consulta_cancelada"
        n.titulo = "Consulta cancelada"
        n.mensagem = mensagem
        n.consulta_id = c.id
        db.session.add(n)

    if u_prof:
        n2 = Notificacao()
        n2.usuario_id = u_prof.id
        n2.tipo = "consulta_cancelada"
        n2.titulo = "Consulta cancelada da sua agenda"
        n2.mensagem = mensagem
        n2.consulta_id = c.id
        db.session.add(n2)

    db.session.commit()
    return c
