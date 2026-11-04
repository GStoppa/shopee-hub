import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "stoppa-core-secret-key-2026-production"
    DATABASE = os.path.join(BASE_DIR, "stoppa_core.db")

    # Limite máximo de 10MB por requisição (para upload de fotos em lote)
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"