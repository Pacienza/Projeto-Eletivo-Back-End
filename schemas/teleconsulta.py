from marshmallow import Schema, fields
from schemas.common import DateDDMMYYYY, TimeHHMM

class TeleconsultaIn(Schema):
    paciente_id = fields.Integer(required=True)
    profissional_id = fields.Integer(required=True)
    data = DateDDMMYYYY(required=True)
    hora = TimeHHMM(required=True)

class TeleconsultaOut(Schema):
    id = fields.Integer()
    paciente_id = fields.Integer()
    profissional_id = fields.Integer()
    data = DateDDMMYYYY()
    hora = TimeHHMM()
    link = fields.String()
    status = fields.String()
