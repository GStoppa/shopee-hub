import math
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.middlewares.auth_middleware import login_required
from app.models.variant_model import ProductVariant
from app.models.stock_movement_model import StockMovement
from app.utils.helpers import converter_numero

stock_bp = Blueprint("stock", __name__, url_prefix="/stock")

@stock_bp.route("/variant/<int:variant_id>/stock", methods=["POST"])
@login_required
def update_stock(variant_id):
    store_id = session.get("store_id")
    user_id = session.get("user_id")
    destino = request.referrer or url_for("product.list_products")

    try:
        new_stock = converter_numero(request.form.get("stock_quantity"), int, 0)
        raw_reason = request.form.get("reason", "").strip()
        motivo = raw_reason if raw_reason else "Ajuste rápido"

        if new_stock < 0:
            flash("A quantidade em estoque não pode ser negativa.", "danger")
            return redirect(destino)
    except ValueError:
        flash("Valor numérico inválido.", "danger")
        return redirect(destino)

    sucesso = ProductVariant.atualizar_stock(variant_id, store_id, new_stock, user_id=user_id, motivo=motivo)
    if sucesso:
        flash("Estoque atualizado com sucesso.", "success")
    else:
        flash("Variação não encontrada nesta loja.", "danger")
    return redirect(destino)

@stock_bp.route("/movements")
@login_required
def stock_movements():
    store_id = session.get("store_id")
    busca = request.args.get("q", "").strip()
    tipo = request.args.get("tipo", "").strip()
    pagina = max(1, request.args.get("page", 1, type=int))
    por_pagina = 20

    total_itens = StockMovement.contar_por_loja(store_id, busca=busca, tipo=tipo)
    total_paginas = max(1, math.ceil(total_itens / por_pagina))
    if pagina > total_paginas:
        pagina = total_paginas

    offset = (pagina - 1) * por_pagina
    movements = StockMovement.listar_por_loja(
        store_id,
        busca=busca,
        tipo=tipo,
        limite=por_pagina,
        offset=offset
    )

    return render_template(
        "products/movements.html",
        movements=movements,
        variant=None,
        pagina=pagina,
        total_paginas=total_paginas,
        total_itens=total_itens
    )

@stock_bp.route("/variant/<int:variant_id>/history")
@login_required
def variant_history(variant_id):
    store_id = session.get("store_id")
    variant = ProductVariant.buscar_por_id(variant_id, store_id)
    if not variant:
        flash("Variação não encontrada.", "danger")
        return redirect(url_for("product.list_products"))

    pagina = max(1, request.args.get("page", 1, type=int))
    por_pagina = 20

    total_itens = StockMovement.contar_por_variante(variant_id, store_id)
    total_paginas = max(1, math.ceil(total_itens / por_pagina))
    if pagina > total_paginas:
        pagina = total_paginas

    offset = (pagina - 1) * por_pagina
    movements = StockMovement.listar_por_variante(
        variant_id=variant_id,
        store_id=store_id,
        limite=por_pagina,
        offset=offset
    )

    return render_template(
        "products/movements.html",
        movements=movements,
        variant=variant,
        pagina=pagina,
        total_paginas=total_paginas,
        total_itens=total_itens
    )

@stock_bp.route("/variant/<int:variant_id>/movement", methods=["POST"])
@login_required
def create_movement(variant_id):
    store_id = session.get("store_id")
    user_id = session.get("user_id")

    # 1. Validação defensiva de existência da variação
    variant = ProductVariant.buscar_por_id(variant_id, store_id)
    if not variant:
        flash("Variação não encontrada nesta loja.", "danger")
        return redirect(url_for("product.list_products"))

    tipo = request.form.get("movement_type", "entrada").strip()
    raw_reason = request.form.get("reason", "").strip()
    motivo = raw_reason if raw_reason else ("Entrada manual" if tipo == "entrada" else "Ajuste manual")

    # 2. Validação de quantidade e saldo disponível
    try:
        quantidade = converter_numero(request.form.get("quantity"), int, 0)
        
        if quantidade <= 0 and tipo != "ajuste":
            flash("A quantidade deve ser superior a zero para entradas ou saídas.", "danger")
            return redirect(url_for("stock.variant_history", variant_id=variant_id))
            
        if quantidade < 0 and tipo == "ajuste":
            flash("O saldo do ajuste não pode ser negativo.", "danger")
            return redirect(url_for("stock.variant_history", variant_id=variant_id))

        if tipo == "saida" and quantidade > variant.stock_quantity:
            flash(
                f"Saldo insuficiente para saída! A variação possui apenas {variant.stock_quantity} un em estoque, "
                f"mas foi solicitada uma saída de {quantidade} un.",
                "danger"
            )
            return redirect(url_for("stock.variant_history", variant_id=variant_id))

    except ValueError:
        flash("Insira uma quantidade numérica válida.", "danger")
        return redirect(url_for("stock.variant_history", variant_id=variant_id))

    # 3. Execução da movimentação
    sucesso = ProductVariant.registrar_movimento(
        variant_id=variant_id,
        store_id=store_id,
        user_id=user_id,
        tipo=tipo,
        quantidade=quantidade,
        motivo=motivo
    )

    if sucesso:
        flash("Movimentação de estoque registrada com sucesso!", "success")
    else:
        flash("Não foi possível processar a movimentação no banco de dados.", "danger")

    return redirect(url_for("stock.variant_history", variant_id=variant_id))