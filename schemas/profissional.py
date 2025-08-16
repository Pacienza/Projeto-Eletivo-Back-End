from marshmallow import Schema, fields

class ProfissionalIn(Schema):
    nome = fields.String(required=True)
    email = fields.Email(required=False, allow_none=True)
    especialidade = fields.String(required=False, allow_none=True)

class ProfissionalOut(Schema):
    id = fields.Integer()
    nome = fields.String()
    email = fields.Email(allow_none=True)
    especialidade = fields.String(allow_none=True)
