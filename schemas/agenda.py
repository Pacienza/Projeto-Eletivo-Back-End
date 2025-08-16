from marshmallow import Schema, fields
from schemas.common import DateDDMMYYYY, TimeHHMM

class AgendaIn(Schema):
    profissional_id = fields.Integer(required=True)
    data = DateDDMMYYYY(required=True)
    hora = TimeHHMM(required=True)

class AgendaOut(Schema):
    id = fields.Integer()
    profissional_id = fields.Integer()
    data = DateDDMMYYYY()
    hora = TimeHHMM()
    disponivel = fields.Boolean()
