from extensions import db
from sqlalchemy import UniqueConstraint
from utils.dates import now_utc

class Consulta(db.Model):
    __tablename__ = "consulta"
    __table_args__ = (
        UniqueConstraint("profissional_id", "data", "hora", "status_open", name="uq_consulta_slot_aberta"),
    )

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey("paciente.id"), nullable=False, index=True)
    profissional_id = db.Column(db.Integer, db.ForeignKey("profissional.id"), nullable=False, index=True)
    data = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default="agendada", nullable=False)  # agendada | cancelada
    criado_em = db.Column(db.DateTime(timezone=True), default=now_utc)

    # campo derivado p/ garantir unicidade só para consultas "abertas"
    status_open = db.Column(db.Boolean, default=True, nullable=False)

    paciente = db.relationship("Paciente")
    profissional = db.relationship("Profissional")
