import os
from PIL import Image, ImageDraw, ImageFont

def gerar_logo_horizontal_ajustada(lg_filename, out_filename, is_dark=False):
    pasta_brand = os.path.join("app", "static", "img", "brand")
    caminho_lg = os.path.join(pasta_brand, lg_filename)

    if not os.path.exists(caminho_lg):
        print(f"Arquivo base não encontrado: {caminho_lg}")
        return

    # 1. Carrega e recorta o símbolo original para eliminar qualquer resíduo interno
    simbolo_raw = Image.open(caminho_lg).convert("RGBA")
    simbolo = simbolo_raw.crop(simbolo_raw.getbbox())

    # 2. Escala o símbolo proporcionalmente
    sym_h = 160
    sym_w = int(simbolo.width * (sym_h / simbolo.height))
    simbolo_redim = simbolo.resize((sym_w, sym_h), Image.Resampling.LANCZOS)

    # 3. Tela temporária ampla para desenho
    tela_temp = Image.new("RGBA", (1800, 600), (0, 0, 0, 0))
    start_x = 80
    start_y = 80
    tela_temp.paste(simbolo_redim, (start_x, start_y), simbolo_redim)

    draw = ImageDraw.Draw(tela_temp)

    # Tipografia oficial
    try:
        font_main = ImageFont.truetype("arialbd.ttf", 78)
        font_sub = ImageFont.truetype("arialbd.ttf", 17)
    except:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    cor_stoppa = (255, 255, 255, 255) if is_dark else (15, 23, 42, 255)
    cor_core = (249, 115, 22, 255)
    cor_sub = (148, 163, 184, 255) if is_dark else (100, 116, 139, 255)

    text_x = start_x + sym_w + 36
    text_y = start_y + 14

    # STOPPA
    draw.text((text_x, text_y), "STOPPA ", fill=cor_stoppa, font=font_main)
    bbox_stoppa = font_main.getbbox("STOPPA ")
    w_stoppa = bbox_stoppa[2] - bbox_stoppa[0]

    # CORE
    draw.text((text_x + w_stoppa, text_y), "CORE", fill=cor_core, font=font_main)

    # Subtítulo com tracking balanceado
    sub_texto = "E-COMMERCE MANAGEMENT"
    line1_h = bbox_stoppa[3] - bbox_stoppa[1]
    sub_y = text_y + line1_h + 18
    curr_x = text_x + 2
    tracking = 4.0

    for char in sub_texto:
        draw.text((curr_x, sub_y), char, fill=cor_sub, font=font_sub)
        bbox_c = font_sub.getbbox(char)
        w_c = (bbox_c[2] - bbox_c[0]) if (bbox_c[2] > bbox_c[0]) else 7
        curr_x += w_c + tracking

    # 4. RECORTE EXATO NO BOUNDING BOX (0px de espaço transparente externo)
    bbox_final = tela_temp.getbbox()
    logo_justa = tela_temp.crop(bbox_final)

    caminho_saida = os.path.join(pasta_brand, out_filename)
    logo_justa.save(caminho_saida, "PNG")
    print(f"[OK] Logo gerada com recorte justo ({logo_justa.width}x{logo_justa.height}px): {caminho_saida}")

if __name__ == "__main__":
    gerar_logo_horizontal_ajustada("stoppacore-light-lg.png", "stoppacore-light-H.png", is_dark=False)
    gerar_logo_horizontal_ajustada("stoppacore-dark-lg.png", "stoppacore-dark-H.png", is_dark=True)