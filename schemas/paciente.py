from marshmallow import Schema, fields
from schemas.common import DateDDMMYYYY

class PacienteIn(Schema):
    nome = fields.String(required=True)
    email = fields.Email(required=False, allow_none=True)
    data_nascimento = DateDDMMYYYY(required=False, allow_none=True)

class PacienteOut(Schema):
    id = fields.Integer()
    nome = fields.String()
    email = fields.Email(allow_none=True)
    data_nascimento = DateDDMMYYYY(allow_none=True)
