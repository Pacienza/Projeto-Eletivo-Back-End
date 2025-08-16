from extensions import db
from sqlalchemy import UniqueConstraint
from utils.dates import now_utc

class Agenda(db.Model):
    __tablename__ = "agenda"
    __table_args__ = (
        UniqueConstraint("profissional_id", "data", "hora", name="uq_agenda_slot"),
    )

    id = db.Column(db.Integer, primary_key=True)
    profissional_id = db.Column(db.Integer, db.ForeignKey("profissional.id"), nullable=False, index=True)
    data = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    disponivel = db.Column(db.Boolean, default=True, nullable=False)
    criado_em = db.Column(db.DateTime(timezone=True), default=now_utc)

    profissional = db.relationship("Profissional", backref="agendas")
