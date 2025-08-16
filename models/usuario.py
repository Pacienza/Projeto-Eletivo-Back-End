from extensions import db
from utils.dates import now_utc

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), nullable=False)  # 'paciente' | 'profissional' | 'admin'
    ativo = db.Column(db.Boolean, default=True)

    # vínculos opcionais
    paciente_id = db.Column(db.Integer, db.ForeignKey("paciente.id"), nullable=True)
    profissional_id = db.Column(db.Integer, db.ForeignKey("profissional.id"), nullable=True)

    criado_em = db.Column(db.DateTime(timezone=True), default=now_utc)
