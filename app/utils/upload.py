import os
import time
from flask import current_app

EXTENSOES_PERMITIDAS = {"png", "jpg", "jpeg", "webp"}

def extensao_permitida(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in EXTENSOES_PERMITIDAS

def remover_imagem_produto(caminho_relativo):
    if not caminho_relativo:
        return
    try:
        caminho_absoluto = os.path.join(current_app.static_folder, caminho_relativo)
        if os.path.exists(caminho_absoluto) and os.path.isfile(caminho_absoluto):
            os.remove(caminho_absoluto)
    except Exception as e:
        print(f"Erro ao remover ficheiro ({caminho_relativo}): {e}")

def salvar_imagem_produto(file, prefixo="var", imagem_antiga=None):
    if not file or file.filename == "":
        return None

    if not extensao_permitida(file.filename):
        return None

    ext = file.filename.rsplit(".", 1)[1].lower()
    timestamp = int(time.time() * 1000)
    novo_nome = f"{prefixo}_{timestamp}.{ext}"

    pasta_destino = os.path.join(current_app.static_folder, "uploads", "products")
    os.makedirs(pasta_destino, exist_ok=True)

    caminho_completo = os.path.join(pasta_destino, novo_nome)
    file.save(caminho_completo)

    if imagem_antiga:
        remover_imagem_produto(imagem_antiga)

    return f"uploads/products/{novo_nome}"

def salvar_logo_loja(file, imagem_antiga=None):
    if not file or file.filename == "":
        return None

    if not extensao_permitida(file.filename):
        return None

    ext = file.filename.rsplit(".", 1)[1].lower()
    timestamp = int(time.time() * 1000)
    novo_nome = f"logo_{timestamp}.{ext}"

    pasta_destino = os.path.join(current_app.static_folder, "uploads", "logos")
    os.makedirs(pasta_destino, exist_ok=True)

    caminho_completo = os.path.join(pasta_destino, novo_nome)
    file.save(caminho_completo)

    if imagem_antiga:
        remover_imagem_produto(imagem_antiga)

    return f"uploads/logos/{novo_nome}"