import os
import time
from werkzeug.utils import secure_filename
from config import Config

def allowed_file(filename: str) -> bool:
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def salvar_logo_loja(file, store_id: int, logo_antigo: str = None) -> str:
    if not file or file.filename == "":
        return None

    if not allowed_file(file.filename):
        raise ValueError("Formato não suportado. Envie ficheiros nos formatos PNG, JPG, JPEG ou WEBP.")

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    ext = secure_filename(file.filename).rsplit(".", 1)[1].lower()
    timestamp = int(time.time())
    novo_nome = f"store_{store_id}_{timestamp}.{ext}"
    caminho_absoluto = os.path.join(Config.UPLOAD_FOLDER, novo_nome)

    file.save(caminho_absoluto)

    if logo_antigo:
        caminho_antigo = os.path.join(Config.BASE_DIR, "app", "static", logo_antigo)
        if os.path.exists(caminho_antigo):
            try:
                os.remove(caminho_antigo)
            except OSError:
                pass

    return f"uploads/logos/{novo_nome}"