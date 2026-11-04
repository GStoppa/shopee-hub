import os
import numpy as np
from PIL import Image

def cor_para_alpha(caminho_imagem, cor_fundo_rgb):
    """
    Decompõe matematicamente a cor de fundo de cada pixel.
    Remove fundos externos e internos (miolos de O, P, R, etc.) 
    preservando a suavização natural das bordas sem serrilhado.
    """
    img = Image.open(caminho_imagem).convert("RGBA")
    arr = np.array(img).astype(float)
    rgb = arr[:, :, :3]
    bg = np.array(cor_fundo_rgb).astype(float)

    # Cálculo da opacidade canal a canal
    a_channels = np.zeros_like(rgb)
    for c in range(3):
        if bg[c] < 255:
            mask_gt = rgb[:, :, c] > bg[c]
            a_channels[:, :, c] = np.where(mask_gt, (rgb[:, :, c] - bg[c]) / (255.0 - bg[c]), a_channels[:, :, c])
        if bg[c] > 0:
            mask_lt = rgb[:, :, c] < bg[c]
            a_channels[:, :, c] = np.where(mask_lt, (bg[c] - rgb[:, :, c]) / bg[c], a_channels[:, :, c])

    alpha = np.max(a_channels, axis=2)
    alpha = np.where(alpha < 0.03, 0.0, alpha)

    # Reconstituição das cores sem contaminação do fundo
    fg = np.zeros_like(rgb)
    ativo = alpha > 0.001
    for c in range(3):
        fg[ativo, c] = (rgb[ativo, c] - (1.0 - alpha[ativo]) * bg[c]) / alpha[ativo]
        fg[~ativo, c] = 0.0

    fg = np.clip(fg, 0, 255)
    resultado = Image.fromarray(np.dstack([fg, alpha * 255]).astype(np.uint8), "RGBA")
    resultado.save(caminho_imagem, "PNG")
    print(f"[OK] Fundo e miolos limpos com sucesso: {os.path.basename(caminho_imagem)}")

def executar():
    base = os.path.join(os.path.expanduser("~"), "Downloads", "Stoppa Core")

    # 1. Processa as versões Light (Fundo Branco #FFFFFF)
    pasta_light = os.path.join(base, "Light")
    if os.path.exists(pasta_light):
        for f in os.listdir(pasta_light):
            if f.lower().endswith(".png"):
                cor_para_alpha(os.path.join(pasta_light, f), (255, 255, 255))

    # 2. Processa as versões Dark (Fundo Escuro do Frame do Figma #1E1E1E)
    pasta_dark = os.path.join(base, "Dark")
    if os.path.exists(pasta_dark):
        for f in os.listdir(pasta_dark):
            if f.lower().endswith(".png"):
                cor_para_alpha(os.path.join(pasta_dark, f), (30, 30, 30))

if __name__ == "__main__":
    executar()