import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Utiliza chave definida nas variáveis de ambiente ou uma chave estável de desenvolvimento
    SECRET_KEY = os.environ.get("SECRET_KEY") or "shopee-hub-secret-key-2026-secure-session"
    DATABASE = os.path.join(BASE_DIR, "shopee_hub.db")

    # Limite máximo de 10MB por requisição (acomoda múltiplas imagens em lote na grade)
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

    # Proteção de cookies contra sequestro de sessão e ataques entre sites
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"