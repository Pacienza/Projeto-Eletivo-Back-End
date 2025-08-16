from flask import request
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from extensions import db
from models.auditoria import Auditoria

def audit(acao: str, recurso: str, referencia_id: int | None = None, detalhes: str | None = None):
    usuario_id = None
    role = None
    try:
        verify_jwt_in_request(optional=True)
        claims = get_jwt()
        sub = claims.get("sub")
        usuario_id = int(sub) if sub is not None else None
        role = claims.get("role")
    except Exception:
        pass
    a = Auditoria()
    a.usuario_id = usuario_id
    a.role = role
    a.recurso = recurso
    a.acao = acao
    a.referencia_id = referencia_id
    a.ip = request.remote_addr
    a.detalhes = detalhes
    db.session.add(a)
    db.session.commit()
