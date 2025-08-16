from marshmallow import Schema, fields
from schemas.common import DateDDMMYYYY

class ProntuarioIn(Schema):
    paciente_id = fields.Integer(required=True)
    data = DateDDMMYYYY(required=True)
    resumo = fields.String(required=True)
    anotacoes = fields.String(allow_none=True)

class ProntuarioOut(Schema):
    id = fields.Integer()
    paciente_id = fields.Integer()
    profissional_id = fields.Integer()
    data = DateDDMMYYYY()
    resumo = fields.String()
    anotacoes = fields.String(allow_none=True)
