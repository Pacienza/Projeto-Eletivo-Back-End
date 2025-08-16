from extensions import db
from utils.dates import now_utc

class Prontuario(db.Model):
    __tablename__ = "prontuario"

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey("paciente.id"), nullable=False, index=True)
    profissional_id = db.Column(db.Integer, db.ForeignKey("profissional.id"), nullable=False, index=True)
    data = db.Column(db.Date, nullable=False)
    resumo = db.Column(db.String(255), nullable=False)
    anotacoes = db.Column(db.Text, nullable=True)

    criado_em = db.Column(db.DateTime(timezone=True), default=now_utc)

    paciente = db.relationship("Paciente")
    profissional = db.relationship("Profissional")
