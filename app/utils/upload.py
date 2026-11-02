import os
import time
import uuid
from flask import current_app

EXTENSOES_PERMITIDAS = {"png", "jpg", "jpeg", "webp"}

def extensao_permitida(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in EXTENSOES_PERMITIDAS

def validar_cabecalho_imagem(file) -> bool:
    """
    Inspeciona a assinatura binária (magic bytes) do cabeçalho do arquivo
    para assegurar que se trata de uma imagem genuína (PNG, JPEG ou WEBP).
    """
    try:
        header = file.read(16)
        file.seek(0)  # Rebobina o ponteiro para permitir o salvamento completo

        if len(header) < 12:
            return False

        # Assinatura PNG (\x89PNG\r\n\x1a\n)
        if header.startswith(b"\x89PNG\r\n\x1a\n"):
            return True

        # Assinatura JPEG / JPG (\xff\xd8\xff)
        if header.startswith(b"\xff\xd8\xff"):
            return True

        # Assinatura WEBP (RIFF....WEBP)
        if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
            return True

        return False
    except Exception:
        return False

def remover_imagem_produto(caminho_relativo: str) -> None:
    """
    Remove fisicamente o arquivo de imagem do disco caso exista.
    """
    if not caminho_relativo:
        return
    try:
        caminho_absoluto = os.path.join(current_app.static_folder, caminho_relativo)
        if os.path.exists(caminho_absoluto) and os.path.isfile(caminho_absoluto):
            os.remove(caminho_absoluto)
    except Exception as e:
        print(f"Erro ao remover arquivo ({caminho_relativo}): {e}")

def salvar_imagem_produto(file, prefixo="var", imagem_antiga=None) -> str:
    """
    Valida e salva a imagem do produto em uploads/products/ com nome único.
    """
    if not file or file.filename == "":
        return None

    if not extensao_permitida(file.filename):
        raise ValueError(
            f"Extensão não suportada no arquivo '{file.filename}'. Utilize apenas PNG, JPG, JPEG ou WEBP."
        )

    if not validar_cabecalho_imagem(file):
        raise ValueError(
            f"O arquivo '{file.filename}' não é uma imagem válida ou está corrompido."
        )

    ext = file.filename.rsplit(".", 1)[1].lower()
    timestamp = int(time.time() * 1000)
    token = uuid.uuid4().hex[:6]
    novo_nome = f"{prefixo}_{timestamp}_{token}.{ext}"

    pasta_destino = os.path.join(current_app.static_folder, "uploads", "products")
    os.makedirs(pasta_destino, exist_ok=True)

    caminho_completo = os.path.join(pasta_destino, novo_nome)
    file.save(caminho_completo)

    if imagem_antiga:
        remover_imagem_produto(imagem_antiga)

    return f"uploads/products/{novo_nome}"

def salvar_logo_loja(file, imagem_antiga=None) -> str:
    """
    Valida e salva o logotipo da loja em uploads/logos/ com nome único garantido.
    """
    if not file or file.filename == "":
        return None

    if not extensao_permitida(file.filename):
        raise ValueError("Extensão não suportada no logotipo. Utilize apenas PNG, JPG, JPEG ou WEBP.")

    if not validar_cabecalho_imagem(file):
        raise ValueError("O arquivo enviado para o logotipo não é uma imagem válida.")

    ext = file.filename.rsplit(".", 1)[1].lower()
    timestamp = int(time.time() * 1000)
    token = uuid.uuid4().hex[:6]
    novo_nome = f"logo_{timestamp}_{token}.{ext}"

    pasta_destino = os.path.join(current_app.static_folder, "uploads", "logos")
    os.makedirs(pasta_destino, exist_ok=True)

    caminho_completo = os.path.join(pasta_destino, novo_nome)
    file.save(caminho_completo)

    if imagem_antiga:
        remover_imagem_produto(imagem_antiga)

    return f"uploads/logos/{novo_nome}"