from extensions import db
from utils.dates import now_utc

class TeleAnexo(db.Model):
    __tablename__ = "tele_anexo"

    id = db.Column(db.Integer, primary_key=True)
    teleconsulta_id = db.Column(db.Integer, db.ForeignKey("teleconsulta.id"), nullable=False, index=True)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    caminho = db.Column(db.String(512), nullable=False)
    mimetype = db.Column(db.String(100), nullable=False)
    tamanho = db.Column(db.Integer, nullable=False)
    criado_em = db.Column(db.DateTime(timezone=True), default=now_utc)

    teleconsulta = db.relationship("Teleconsulta", backref="anexos")
