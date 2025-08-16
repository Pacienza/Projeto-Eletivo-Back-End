from marshmallow import Schema, fields
from schemas.common import DateDDMMYYYY, TimeHHMM

class ConsultaIn(Schema):
    paciente_id = fields.Integer(required=True)
    profissional_id = fields.Integer(required=True)
    data = DateDDMMYYYY(required=True)
    hora = TimeHHMM(required=True)

class ConsultaOut(Schema):
    id = fields.Integer()
    paciente_id = fields.Integer()
    profissional_id = fields.Integer()
    data = DateDDMMYYYY()
    hora = TimeHHMM()
    status = fields.String()
