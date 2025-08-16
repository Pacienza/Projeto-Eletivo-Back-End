from marshmallow import Schema, fields
from schemas.common import DateDDMMYYYY

class PrescricaoIn(Schema):
    paciente_id = fields.Integer(required=True)
    data = DateDDMMYYYY(required=True)
    texto = fields.String(required=True)

class PrescricaoOut(Schema):
    id = fields.Integer()
    paciente_id = fields.Integer()
    profissional_id = fields.Integer()
    data = DateDDMMYYYY()
    texto = fields.String()
