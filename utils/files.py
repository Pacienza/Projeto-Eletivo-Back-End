import os
from werkzeug.utils import secure_filename

def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def save_upload(file_storage, base_dir: str):
    """Salva um arquivo vindo de request.files e retorna (path, nome, mimetype, tamanho)."""
    ensure_dir(base_dir)
    filename = secure_filename(file_storage.filename or "arquivo")
    full_path = os.path.join(base_dir, filename)

    # evita sobrescrever
    name, ext = os.path.splitext(filename)
    i = 1
    while os.path.exists(full_path):
        filename = f"{name}_{i}{ext}"
        full_path = os.path.join(base_dir, filename)
        i += 1

    file_storage.save(full_path)
    size = os.path.getsize(full_path)
    return full_path, filename, (file_storage.mimetype or "application/octet-stream"), size
