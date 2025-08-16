from flask_smorest import Blueprint, abort
from flask import request, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db
from models.teleconsulta import Teleconsulta
from models.tele_anexo import TeleAnexo
from models.paciente import Paciente
from models.profissional import Profissional
from models.prontuario import Prontuario
from schemas.teleconsulta import TeleconsultaIn, TeleconsultaOut
from schemas.anexo import AnexoOut
from utils.ids import short_token
from utils.files import save_upload
from utils.dates import now_utc

blp = Blueprint("teleconsultas", __name__, url_prefix="/teleconsultas", description="Teleconsulta")

@blp.route("", methods=["GET"])
@jwt_required()
@blp.response(200, TeleconsultaOut(many=True))
def listar():
    claims = get_jwt()
    role = claims.get("role")
    pac_id_claim = claims.get("paciente_id")
    prof_id_claim = claims.get("profissional_id")

    q = Teleconsulta.query
    if role == "paciente":
        q = q.filter(Teleconsulta.paciente_id == pac_id_claim)
    elif role == "profissional":
        q = q.filter(Teleconsulta.profissional_id == prof_id_claim)
    # admin: sem filtro
    return q.order_by(Teleconsulta.data.desc(), Teleconsulta.hora.desc()).all()

@blp.route("", methods=["POST"])
@jwt_required()
@blp.arguments(TeleconsultaIn)
@blp.response(201, TeleconsultaOut)
def criar(payload):
    claims = get_jwt()
    role = claims.get("role")
    pac_id_token = claims.get("paciente_id")
    prof_id_token = claims.get("profissional_id")

    # RBAC
    if role == "paciente" and payload["paciente_id"] != pac_id_token:
        abort(403, message="Paciente só pode agendar teleconsulta para si")
    if role == "profissional" and payload["profissional_id"] != prof_id_token:
        abort(403, message="Profissional só pode agendar na própria agenda")

    if not Paciente.query.get(payload["paciente_id"]):
        abort(400, message="Paciente inválido")
    if not Profissional.query.get(payload["profissional_id"]):
        abort(400, message="Profissional inválido")

    t = Teleconsulta()
    t.paciente_id = payload["paciente_id"]
    t.profissional_id = payload["profissional_id"]
    t.data = payload["data"]
    t.hora = payload["hora"]
    t.link = current_app.config["TELE_BASE_URL"].rstrip("/") + "/" + short_token(12)
    t.status = "agendada"

    db.session.add(t)
    db.session.commit()
    return t

@blp.route("/<int:tid>/finalizar", methods=["PATCH"])
@jwt_required()
@blp.response(200, TeleconsultaOut)
def finalizar(tid: int):
    """Finaliza a teleconsulta. Profissional pode opcionalmente gerar um registro no prontuário via query string:
       ?resumo=...&anotacoes=...&data=dd/mm/aaaa (data opcional; default = data da tele)."""
    claims = get_jwt()
    role = claims.get("role")
    prof_id_token = claims.get("profissional_id")

    t = Teleconsulta.query.get(tid)
    if not t:
        abort(404, message="Teleconsulta não encontrada")

    if role == "profissional" and t.profissional_id != prof_id_token:
        abort(403, message="Você só pode finalizar suas próprias teleconsultas")
    if role not in ("profissional", "admin"):
        abort(403, message="Apenas profissional ou admin")

    if t.status == "cancelada":
        abort(409, message="Teleconsulta já cancelada")
    t.status = "finalizada"

    # registro em prontuário (RF013) opcional via query
    from schemas.common import DateDDMMYYYY
    resumo = request.args.get("resumo")
    anotacoes = request.args.get("anotacoes")
    data_str = request.args.get("data")  # dd/mm/aaaa
    data_reg = t.data
    if data_str:
        try:
            data_reg = DateDDMMYYYY()._deserialize(data_str, "data", None)
        except Exception:
            abort(400, message="data inválida, use dd/mm/aaaa")

    if resumo:
        p = Prontuario()
        p.paciente_id = t.paciente_id
        p.profissional_id = t.profissional_id
        p.data = data_reg
        p.resumo = resumo
        p.anotacoes = anotacoes
        db.session.add(p)

    db.session.commit()
    return t

@blp.route("/<int:tid>/cancelar", methods=["PATCH"])
@jwt_required()
@blp.response(200, TeleconsultaOut)
def cancelar(tid: int):
    claims = get_jwt()
    role = claims.get("role")
    pac_id_token = claims.get("paciente_id")
    prof_id_token = claims.get("profissional_id")

    t = Teleconsulta.query.get(tid)
    if not t:
        abort(404, message="Teleconsulta não encontrada")

    if role == "paciente" and t.paciente_id != pac_id_token:
        abort(403, message="Paciente só pode cancelar a própria teleconsulta")
    if role == "profissional" and t.profissional_id != prof_id_token:
        abort(403, message="Profissional só pode cancelar teleconsultas próprias")

    t.status = "cancelada"
    db.session.commit()
    return t

# -------- Anexos --------

@blp.route("/<int:tid>/anexos", methods=["POST"])
@jwt_required()
@blp.response(201, AnexoOut(many=True))
def upload_anexos(tid: int):
    """Aceita multipart/form-data com campo 'files' (um ou mais)."""
    claims = get_jwt()
    role = claims.get("role")
    pac_id_token = claims.get("paciente_id")
    prof_id_token = claims.get("profissional_id")

    t = Teleconsulta.query.get(tid)
    if not t:
        abort(404, message="Teleconsulta não encontrada")

    if role == "paciente" and t.paciente_id != pac_id_token:
        abort(403, message="Paciente só pode enviar anexos da própria teleconsulta")
    if role == "profissional" and t.profissional_id != prof_id_token:
        abort(403, message="Profissional só pode enviar anexos das próprias teleconsultas")

    files = request.files.getlist("files")
    if not files:
        abort(400, message="Envie arquivos no campo 'files'")

    base_dir = current_app.config["UPLOAD_DIR"]
    created = []
    for f in files:
        path, fname, mimetype, size = save_upload(f, base_dir)
        a = TeleAnexo()
        a.teleconsulta_id = t.id
        a.nome_arquivo = fname
        a.caminho = path
        a.mimetype = mimetype
        a.tamanho = size
        db.session.add(a)
        created.append(a)

    db.session.commit()
    return created

@blp.route("/<int:tid>/anexos", methods=["GET"])
@jwt_required()
@blp.response(200, AnexoOut(many=True))
def listar_anexos(tid: int):
    claims = get_jwt()
    role = claims.get("role")
    pac_id_token = claims.get("paciente_id")
    prof_id_token = claims.get("profissional_id")

    t = Teleconsulta.query.get(tid)
    if not t:
        abort(404, message="Teleconsulta não encontrada")

    if role == "paciente" and t.paciente_id != pac_id_token:
        abort(403, message="Acesso negado")
    if role == "profissional" and t.profissional_id != prof_id_token:
        abort(403, message="Acesso negado")

    return TeleAnexo.query.filter_by(teleconsulta_id=tid).order_by(TeleAnexo.id.desc()).all()

@blp.route("/anexos/<int:aid>/download", methods=["GET"])
@jwt_required()
def download_anexo(aid: int):
    a = TeleAnexo.query.get(aid)
    if not a:
        abort(404, message="Anexo não encontrado")
    # autorização: precisa pertencer a uma teleconsulta do usuário atual
    claims = get_jwt()
    role = claims.get("role")
    pac_id_token = claims.get("paciente_id")
    prof_id_token = claims.get("profissional_id")

    t = a.teleconsulta
    if role == "paciente" and t.paciente_id != pac_id_token:
        abort(403, message="Acesso negado")
    if role == "profissional" and t.profissional_id != prof_id_token:
        abort(403, message="Acesso negado")

    return send_file(a.caminho, as_attachment=True, download_name=a.nome_arquivo)
