import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "chave-secreta-padrao-dev")
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, "shopee_hub.db")

    # Configurações de Upload de Imagens
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads", "logos")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # Limite máximo de 2MB por requisição
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}