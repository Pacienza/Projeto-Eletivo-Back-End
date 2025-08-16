from extensions import db
from utils.dates import now_utc

class Notificacao(db.Model):
    __tablename__ = "notificacao"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False, index=True)
    tipo = db.Column(db.String(50), nullable=False)        # ex: "consulta_agendada", "consulta_cancelada"
    titulo = db.Column(db.String(150), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    lido = db.Column(db.Boolean, default=False, nullable=False)

    consulta_id = db.Column(db.Integer, db.ForeignKey("consulta.id"), nullable=True)
    criado_em = db.Column(db.DateTime(timezone=True), default=now_utc)
