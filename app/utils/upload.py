import os
import time
from werkzeug.utils import secure_filename
from config import Config

def allowed_file(filename: str) -> bool:
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def remover_ficheiro_antigo(caminho_relativo: str):
    if not caminho_relativo:
        return
    caminho_limpo = caminho_relativo.replace("\\", "/").lstrip("/")
    caminho_absoluto = os.path.join(Config.BASE_DIR, "app", "static", caminho_limpo)
    if os.path.exists(caminho_absoluto):
        try:
            os.remove(caminho_absoluto)
        except OSError:
            pass

def salvar_logo_loja(file, store_id: int, logo_antigo: str = None) -> str:
    if not file or file.filename == "":
        return None

    if not allowed_file(file.filename):
        raise ValueError("Formato não suportado. Utilize ficheiros PNG, JPG, JPEG ou WEBP.")

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    ext = file.filename.rsplit(".", 1)[1].lower()
    timestamp = int(time.time())
    novo_nome = f"store_{store_id}_{timestamp}.{ext}"
    caminho_absoluto = os.path.join(Config.UPLOAD_FOLDER, novo_nome)

    file.save(caminho_absoluto)

    if logo_antigo:
        remover_ficheiro_antigo(logo_antigo)

    return f"uploads/logos/{novo_nome}"

def salvar_imagem_produto(file, prefixo: str = "prod", imagem_antiga: str = None) -> str:
    if not file or file.filename == "":
        return None

    if not allowed_file(file.filename):
        raise ValueError("Formato não suportado. Utilize ficheiros PNG, JPG, JPEG ou WEBP.")

    os.makedirs(Config.UPLOAD_PRODUCTS_FOLDER, exist_ok=True)

    ext = file.filename.rsplit(".", 1)[1].lower()
    timestamp = int(time.time() * 1000)
    novo_nome = f"{prefixo}_{timestamp}.{ext}"
    caminho_absoluto = os.path.join(Config.UPLOAD_PRODUCTS_FOLDER, novo_nome)

    file.save(caminho_absoluto)

    if imagem_antiga:
        remover_ficheiro_antigo(imagem_antiga)

    return f"uploads/products/{novo_nome}"