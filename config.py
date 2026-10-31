import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "shopee-hub-secret-key-2026"
    DATABASE = os.path.join(BASE_DIR, "shopee_hub.db")
    MAX_CONTENT_LENGTH = 6 * 1024 * 1024  # Limite máximo de 2MB para uploads

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"