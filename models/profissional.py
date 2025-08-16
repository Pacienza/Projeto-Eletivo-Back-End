from extensions import db
from utils.dates import now_utc

class Profissional(db.Model):
    __tablename__ = "profissional"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255), unique=True, index=True)
    especialidade = db.Column(db.String(120))
    criado_em = db.Column(db.DateTime(timezone=True), default=now_utc)

    def __repr__(self):
        return f"<Profissional {self.id} - {self.nome}>"
