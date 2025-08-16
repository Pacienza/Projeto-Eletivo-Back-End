from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.notificacao import Notificacao
from schemas.notificacao import NotificacaoOut, NotificacaoReadIn

blp = Blueprint("notificacoes", __name__, url_prefix="/notificacoes", description="Notificações")

@blp.route("", methods=["GET"])
@jwt_required()
@blp.response(200, NotificacaoOut(many=True))
def minhas_notificacoes():
    user_id = int(get_jwt_identity())  # identity é string → converte para int
    return (
        Notificacao.query
        .filter_by(usuario_id=user_id)
        .order_by(Notificacao.id.desc())
        .all()
    )

@blp.route("/<int:notif_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(NotificacaoReadIn)
@blp.response(200, NotificacaoOut)
def marcar_lido(payload, notif_id):
    user_id = int(get_jwt_identity())
    n = Notificacao.query.get(notif_id)
    if not n or n.usuario_id != user_id:
        abort(404, message="Notificação não encontrada")
    n.lido = bool(payload["lido"])
    db.session.commit()
    return n
