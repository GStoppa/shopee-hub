def converter_numero(valor, tipo=float, padrao=0.0):
    """
    Converte valores monetários ou numéricos formatados no padrão brasileiro
    (com vírgula, prefixo R$ e espaços) para float ou int de forma defensiva.
    """
    if valor is None:
        return padrao
    limpo = str(valor).strip().replace("R$", "").replace(" ", "")
    if limpo == "":
        return padrao
    if "," in limpo and "." in limpo:
        limpo = limpo.replace(".", "").replace(",", ".")
    elif "," in limpo:
        limpo = limpo.replace(",", ".")
    try:
        resultado = tipo(limpo)
        return max(resultado, tipo(0))
    except (ValueError, TypeError):
        return padrao