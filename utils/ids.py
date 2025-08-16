import secrets
def short_token(n: int = 22) -> str:
    return secrets.token_urlsafe(n)
