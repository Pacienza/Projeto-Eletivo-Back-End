from extensions import db
from utils.dates import now_utc

class Prescricao(db.Model):
    __tablename__ = "prescricao"

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey("paciente.id"), nullable=False, index=True)
    profissional_id = db.Column(db.Integer, db.ForeignKey("profissional.id"), nullable=False, index=True)
    data = db.Column(db.Date, nullable=False)
    texto = db.Column(db.Text, nullable=False)

    criado_em = db.Column(db.DateTime(timezone=True), default=now_utc)

    paciente = db.relationship("Paciente")
    profissional = db.relationship("Profissional")
