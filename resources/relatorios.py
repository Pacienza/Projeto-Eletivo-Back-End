from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from flask import request
from sqlalchemy import func, select
from extensions import db
from models.consulta import Consulta
from models.teleconsulta import Teleconsulta
from models.profissional import Profissional
from models.internacao import Internacao
from schemas.common import DateDDMMYYYY
from utils.rbac import roles_required

blp = Blueprint("relatorios", __name__, url_prefix="/relatorios", description="Relatórios (admin)")


def parse_periodo():
    inicio_s = request.args.get("inicio")
    fim_s = request.args.get("fim")
    if not inicio_s or not fim_s:
        abort(400, message="Informe ?inicio=dd/mm/aaaa&fim=dd/mm/aaaa")
    di = DateDDMMYYYY()._deserialize(inicio_s, "inicio", None)
    df = DateDDMMYYYY()._deserialize(fim_s, "fim", None)
    return di, df


@blp.route("/consultas_por_periodo", methods=["GET"])
@jwt_required()
@roles_required("admin")
def consultas_por_periodo():
    di, df = parse_periodo()

    stmt_ag = (
        select(func.count())
        .select_from(Consulta)
        .where(Consulta.data >= di, Consulta.data <= df, Consulta.status == "agendada")
    )
    stmt_ca = (
        select(func.count())
        .select_from(Consulta)
        .where(Consulta.data >= di, Consulta.data <= df, Consulta.status == "cancelada")
    )

    total_agendadas = db.session.execute(stmt_ag).scalar_one_or_none() or 0
    total_canceladas = db.session.execute(stmt_ca).scalar_one_or_none() or 0

    return {
        "inicio": di.strftime("%d/%m/%Y"),
        "fim": df.strftime("%d/%m/%Y"),
        "total_agendadas": int(total_agendadas),
        "total_canceladas": int(total_canceladas),
    }


@blp.route("/atendimentos_por_profissional", methods=["GET"])
@jwt_required()
@roles_required("admin")
def atendimentos_por_profissional():
    di, df = parse_periodo()

    consultas_q = (
        select(Consulta.profissional_id, func.count().label("qtd"))
        .where(Consulta.data >= di, Consulta.data <= df)
        .group_by(Consulta.profissional_id)
        .subquery()
    )

    tele_q = (
        select(Teleconsulta.profissional_id, func.count().label("qtd"))
        .where(
            Teleconsulta.data >= di,
            Teleconsulta.data <= df,
            Teleconsulta.status == "finalizada",
        )
        .group_by(Teleconsulta.profissional_id)
        .subquery()
    )

    stmt = (
        select(
            Profissional.id,
            Profissional.nome,
            func.coalesce(consultas_q.c.qtd, 0),
            func.coalesce(tele_q.c.qtd, 0),
        )
        .outerjoin(consultas_q, consultas_q.c.profissional_id == Profissional.id)
        .outerjoin(tele_q, tele_q.c.profissional_id == Profissional.id)
        .order_by(Profissional.nome.asc())
    )

    rows = db.session.execute(stmt).all()
    return [
        {
            "profissional_id": r[0],
            "nome": r[1],
            "consultas": int(r[2] or 0),
            "teleconsultas_finalizadas": int(r[3] or 0),
        }
        for r in rows
    ]


@blp.route("/internacoes_por_periodo", methods=["GET"])
@jwt_required()
@roles_required("admin")
def internacoes_por_periodo():
    di, df = parse_periodo()

    stmt_adm = (
        select(func.count())
        .select_from(Internacao)
        .where(Internacao.data_entrada >= di, Internacao.data_entrada <= df)
    )
    stmt_altas = (
        select(func.count())
        .select_from(Internacao)
        .where(
            Internacao.data_alta.isnot(None),
            Internacao.data_alta >= di,
            Internacao.data_alta <= df,
        )
    )

    admitidos = db.session.execute(stmt_adm).scalar_one_or_none() or 0
    altas = db.session.execute(stmt_altas).scalar_one_or_none() or 0

    return {
        "inicio": di.strftime("%d/%m/%Y"),
        "fim": df.strftime("%d/%m/%Y"),
        "admitidos": int(admitidos),
        "altas": int(altas),
    }


@blp.route("/tempo_medio_internacao", methods=["GET"])
@jwt_required()
@roles_required("admin")
def tempo_medio_internacao():
    di, df = parse_periodo()

    # Média em dias das internações com alta no período (SQLite: julianday)
    stmt = select(
        (func.julianday(Internacao.data_alta) - func.julianday(Internacao.data_entrada)).label("dias")
    ).where(
        Internacao.data_alta.isnot(None),
        Internacao.data_alta >= di,
        Internacao.data_alta <= df,
    )

    rows = db.session.execute(stmt).all()
    valores = [row[0] for row in rows if row[0] is not None]
    media = (sum(valores) / len(valores)) if valores else 0.0

    return {
        "inicio": di.strftime("%d/%m/%Y"),
        "fim": df.strftime("%d/%m/%Y"),
        "media_dias": round(float(media), 2),
    }
