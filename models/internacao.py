from extensions import db
from utils.dates import now_utc

class Internacao(db.Model):
    __tablename__ = "internacao"

    id = db.Column(db.Integer, primary_key=True)

    paciente_id = db.Column(db.Integer, db.ForeignKey("paciente.id"), nullable=False, index=True)
    profissional_id = db.Column(db.Integer, db.ForeignKey("profissional.id"), nullable=False, index=True)

    leito = db.Column(db.String(50), nullable=True)
    diagnostico = db.Column(db.String(255), nullable=True)

    data_entrada = db.Column(db.Date, nullable=False)
    data_alta = db.Column(db.Date, nullable=True)

    status = db.Column(db.String(20), default="admitido", nullable=False)  # admitido | alta
    criado_em = db.Column(db.DateTime(timezone=True), default=now_utc)

    paciente = db.relationship("Paciente")
    profissional = db.relationship("Profissional")
