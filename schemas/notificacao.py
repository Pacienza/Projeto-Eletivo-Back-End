from marshmallow import Schema, fields

class NotificacaoOut(Schema):
    id = fields.Integer()
    usuario_id = fields.Integer()
    tipo = fields.String()
    titulo = fields.String()
    mensagem = fields.String()
    lido = fields.Boolean()
    criado_em = fields.String()

class NotificacaoReadIn(Schema):
    lido = fields.Boolean(required=True)
