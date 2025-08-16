from extensions import db
from utils.dates import now_utc

class Auditoria(db.Model):
    __tablename__ = "auditoria"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, index=True, nullable=True)
    role = db.Column(db.String(20), nullable=True)

    recurso = db.Column(db.String(80), nullable=False)       
    acao = db.Column(db.String(20), nullable=False)          # CREATE | UPDATE | DELETE | LOGIN
    referencia_id = db.Column(db.Integer, nullable=True)     # id do recurso afetado

    ip = db.Column(db.String(45), nullable=True)
    detalhes = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime(timezone=True), default=now_utc)
