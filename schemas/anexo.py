from marshmallow import Schema, fields

class AnexoOut(Schema):
    id = fields.Integer()
    teleconsulta_id = fields.Integer()
    nome_arquivo = fields.String()
    mimetype = fields.String()
    tamanho = fields.Integer()
    criado_em = fields.String()
