from extensions import db
from utils.dates import now_utc

class Teleconsulta(db.Model):
    __tablename__ = "teleconsulta"

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey("paciente.id"), nullable=False, index=True)
    profissional_id = db.Column(db.Integer, db.ForeignKey("profissional.id"), nullable=False, index=True)
    data = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)

    link = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default="agendada", nullable=False)  # agendada | finalizada | cancelada
    criado_em = db.Column(db.DateTime(timezone=True), default=now_utc)

    paciente = db.relationship("Paciente")
    profissional = db.relationship("Profissional")
