import os
from app import create_app
from config import Config
from init_db import inicializar_banco

app = create_app()

if __name__ == "__main__":
    if not os.path.exists(Config.DATABASE):
        print("Banco de dados não encontrado. Criando tabelas e registros iniciais...")
        inicializar_banco()
        
    app.run(debug=True)