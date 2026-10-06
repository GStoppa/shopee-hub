#Interação com o sistema operacional
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "william-n-esquece-da-garota-confusa")
    DB_PATH = os.path.join(BASE_DIR, "shopee_hub.db")