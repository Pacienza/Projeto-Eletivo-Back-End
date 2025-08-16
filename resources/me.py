from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt
from models.consulta import Consulta
from models.teleconsulta import Teleconsulta
from models.prontuario import Prontuario
from models.prescricao import Prescricao
from models.internacao import Internacao

blp = Blueprint("me", __name__, url_prefix="/me", description="Minha conta")

@blp.route("/historico", methods=["GET"])
@jwt_required()
def historico():
    claims = get_jwt()
    role = claims.get("role")
    if role != "paciente":
        return {"message": "Apenas paciente"}, 403
    pac_id = claims.get("paciente_id")

    consultas = Consulta.query.filter_by(paciente_id=pac_id).order_by(Consulta.data.desc(), Consulta.hora.desc()).all()
    teles = Teleconsulta.query.filter_by(paciente_id=pac_id).order_by(Teleconsulta.data.desc(), Teleconsulta.hora.desc()).all()
    pronts = Prontuario.query.filter_by(paciente_id=pac_id).order_by(Prontuario.data.desc(), Prontuario.id.desc()).all()
    prescs = Prescricao.query.filter_by(paciente_id=pac_id).order_by(Prescricao.data.desc(), Prescricao.id.desc()).all()

    # serialização simples (sem schemas para mix)
    def consulta_to_dict(c):
        return {"id": c.id, "data": c.data.strftime("%d/%m/%Y"), "hora": c.hora.strftime("%H:%M"),
                "profissional_id": c.profissional_id, "status": c.status}
    def tele_to_dict(t):
        return {"id": t.id, "data": t.data.strftime("%d/%m/%Y"), "hora": t.hora.strftime("%H:%M"),
                "profissional_id": t.profissional_id, "status": t.status, "link": t.link}
    def pront_to_dict(p):
        return {"id": p.id, "data": p.data.strftime("%d/%m/%Y"), "profissional_id": p.profissional_id,
                "resumo": p.resumo}
    def presc_to_dict(p):
        return {"id": p.id, "data": p.data.strftime("%d/%m/%Y"), "profissional_id": p.profissional_id,
                "texto": p.texto}

    return {
        "consultas": [consulta_to_dict(c) for c in consultas],
        "teleconsultas": [tele_to_dict(t) for t in teles],
        "prontuarios": [pront_to_dict(p) for p in pronts],
        "prescricoes": [presc_to_dict(p) for p in prescs],
    }
