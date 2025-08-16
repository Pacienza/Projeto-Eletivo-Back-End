from marshmallow import Schema, fields
from schemas.common import DateDDMMYYYY

class InternacaoIn(Schema):
    paciente_id = fields.Integer(required=True)
    data_entrada = DateDDMMYYYY(required=True)
    leito = fields.String(allow_none=True)
    diagnostico = fields.String(allow_none=True)

class InternacaoOut(Schema):
    id = fields.Integer()
    paciente_id = fields.Integer()
    profissional_id = fields.Integer()
    leito = fields.String(allow_none=True)
    diagnostico = fields.String(allow_none=True)
    data_entrada = DateDDMMYYYY()
    data_alta = DateDDMMYYYY(allow_none=True)
    status = fields.String()

class InternacaoAltaIn(Schema):
    data_alta = DateDDMMYYYY(required=True)

class InternacaoUpdateIn(Schema):
    leito = fields.String(allow_none=True)
    diagnostico = fields.String(allow_none=True)
