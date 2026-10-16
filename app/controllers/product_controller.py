import math
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.database import DatabaseConnection
from app.middlewares.auth_middleware import login_required, role_required
from app.models.product_model import Product, ProductVariant, StockMovement
from app.models.category_model import Category
from app.utils.upload import salvar_imagem_produto, remover_imagem_produto

product_bp = Blueprint("product", __name__, url_prefix="/products")

def converter_numero(valor, tipo=float, padrao=0.0):
    if valor is None:
        return padrao
    limpo = str(valor).strip().replace("R$", "").replace(" ", "")
    if "," in limpo and "." in limpo:
        limpo = limpo.replace(".", "").replace(",", ".")
    elif "," in limpo:
        limpo = limpo.replace(",", ".")
    try:
        return max(tipo(limpo), tipo(0))
    except (ValueError, TypeError):
        return padrao

@product_bp.route("/")
@login_required
def list_products():
    store_id = session.get("store_id")
    busca = request.args.get("q", "").strip()
    cat_id = request.args.get("category_id", type=int)
    status = request.args.get("status", "").strip()
    pagina = max(1, request.args.get("page", 1, type=int))
    por_pagina = 10

    total_itens = Product.contar_por_loja(store_id, busca=busca, category_id=cat_id, status=status)
    total_paginas = max(1, math.ceil(total_itens / por_pagina))
    if pagina > total_paginas:
        pagina = total_paginas

    offset = (pagina - 1) * por_pagina
    products = Product.listar_por_loja(
        store_id, busca=busca, category_id=cat_id, status=status,
        limite=por_pagina, offset=offset
    )
    categories = Category.listar_por_loja(store_id)

    return render_template(
        "products/list.html",
        products=products,
        categories=categories,
        pagina=pagina,
        total_paginas=total_paginas,
        total_itens=total_itens
    )

@product_bp.route("/novo", methods=["GET", "POST"])
@login_required
@role_required(["owner", "manager"])
def create_product():
    store_id = session.get("store_id")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category_id = request.form.get("category_id") or None
        description = request.form.get("description", "").strip()
        
        weight_g = converter_numero(request.form.get("weight_g"), float, 0.0)
        length_cm = converter_numero(request.form.get("length_cm"), float, 0.0)
        width_cm = converter_numero(request.form.get("width_cm"), float, 0.0)
        height_cm = converter_numero(request.form.get("height_cm"), float, 0.0)
        is_active = converter_numero(request.form.get("is_active"), int, 1)

        has_variants = request.form.get("has_variants") == "1"

        if not name:
            flash("O nome do produto é obrigatório.", "danger")
            categories = Category.listar_por_loja(store_id)
            return render_template("products/form.html", product=None, categories=categories)

        variantes = []

        if not has_variants:
            sku = request.form.get("simple_sku", "").strip().upper()
            barcode = request.form.get("simple_barcode", "").strip()
            price = converter_numero(request.form.get("simple_price"), float, 0.0)
            cost_price = converter_numero(request.form.get("simple_cost_price"), float, 0.0)
            stock_quantity = converter_numero(request.form.get("simple_stock"), int, 0)
            min_stock = converter_numero(request.form.get("simple_min_stock"), int, 5)

            if not sku:
                flash("O SKU é obrigatório para o produto simples.", "danger")
                categories = Category.listar_por_loja(store_id)
                return render_template("products/form.html", product=None, categories=categories)

            if ProductVariant.sku_existe(sku):
                flash(f"O SKU '{sku}' já está cadastrado em outro produto da loja.", "danger")
                categories = Category.listar_por_loja(store_id)
                return render_template("products/form.html", product=None, categories=categories)

            img_file = request.files.get("simple_image")
            img_url = None
            if img_file and img_file.filename != "":
                img_url = salvar_imagem_produto(img_file, prefixo="var")

            variantes.append(
                ProductVariant(
                    product_id=None,
                    sku=sku,
                    barcode=barcode or None,
                    variant_name="Padrão",
                    cost_price=cost_price,
                    price=price,
                    stock_quantity=stock_quantity,
                    min_stock=min_stock,
                    image_url=img_url
                )
            )
        else:
            row_ids = request.form.getlist("variant_row_id[]")
            v_names = request.form.getlist("variant_name[]")
            v_skus = request.form.getlist("variant_sku[]")
            v_barcodes = request.form.getlist("variant_barcode[]")
            v_costs = request.form.getlist("variant_cost[]")
            v_prices = request.form.getlist("variant_price[]")
            v_stocks = request.form.getlist("variant_stock[]")
            v_min_stocks = request.form.getlist("variant_min_stock[]")

            if not v_skus or len(v_skus) == 0:
                flash("Adicione pelo menos uma variação.", "danger")
                categories = Category.listar_por_loja(store_id)
                return render_template("products/form.html", product=None, categories=categories)

            skus_vistos = set()
            for i in range(len(v_skus)):
                sku = v_skus[i].strip().upper()
                if not sku:
                    continue

                if sku in skus_vistos:
                    flash(f"SKU duplicado na lista de variações: {sku}", "danger")
                    categories = Category.listar_por_loja(store_id)
                    return render_template("products/form.html", product=None, categories=categories)
                skus_vistos.add(sku)

                if ProductVariant.sku_existe(sku):
                    flash(f"O SKU '{sku}' já está cadastrado em outro produto da loja.", "danger")
                    categories = Category.listar_por_loja(store_id)
                    return render_template("products/form.html", product=None, categories=categories)

                row_id = row_ids[i] if i < len(row_ids) else f"row_{i}"
                v_name = v_names[i].strip() if i < len(v_names) else "Variação"
                v_barcode = v_barcodes[i].strip() if i < len(v_barcodes) else ""
                v_cost = converter_numero(v_costs[i], float, 0.0) if i < len(v_costs) else 0.0
                v_price = converter_numero(v_prices[i], float, 0.0) if i < len(v_prices) else 0.0
                v_stock = converter_numero(v_stocks[i], int, 0) if i < len(v_stocks) else 0
                v_min = converter_numero(v_min_stocks[i], int, 5) if i < len(v_min_stocks) else 5

                img_file = request.files.get(f"variant_image_{row_id}")
                img_url = None
                if img_file and img_file.filename != "":
                    img_url = salvar_imagem_produto(img_file, prefixo="var")

                variantes.append(
                    ProductVariant(
                        product_id=None,
                        sku=sku,
                        barcode=v_barcode or None,
                        variant_name=v_name,
                        cost_price=v_cost,
                        price=v_price,
                        stock_quantity=v_stock,
                        min_stock=v_min,
                        image_url=img_url
                    )
                )

        try:
            user_id = session.get("user_id")
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                produto = Product(
                    store_id=store_id,
                    category_id=category_id,
                    name=name,
                    description=description,
                    weight_g=weight_g,
                    length_cm=length_cm,
                    width_cm=width_cm,
                    height_cm=height_cm,
                    is_active=is_active,
                    variants=variantes
                )
                produto.salvar(cursor=cursor)

                for v in produto.variants:
                    if v.stock_quantity > 0:
                        mov = StockMovement(
                            variant_id=v.id,
                            user_id=user_id,
                            movement_type="entrada",
                            quantity=v.stock_quantity,
                            previous_stock=0,
                            resulting_stock=v.stock_quantity,
                            reason="Estoque inicial no cadastro"
                        )
                        mov.salvar(cursor=cursor)

            flash(f"Produto '{name}' cadastrado com sucesso!", "success")
            return redirect(url_for("product.list_products"))
        except Exception as e:
            flash(f"Erro ao cadastrar o produto: {e}", "danger")

    categories = Category.listar_por_loja(store_id)
    return render_template("products/form.html", product=None, categories=categories)

@product_bp.route("/<int:product_id>/editar", methods=["GET", "POST"])
@login_required
@role_required(["owner", "manager"])
def edit_product(product_id):
    store_id = session.get("store_id")
    produto = Product.buscar_por_id(product_id, store_id)

    if not produto:
        flash("Produto não encontrado.", "danger")
        return redirect(url_for("product.list_products"))

    if request.method == "POST":
        user_id = session.get("user_id")
        produto.name = request.form.get("name", "").strip()
        produto.category_id = request.form.get("category_id") or None
        produto.description = request.form.get("description", "").strip()
        
        produto.weight_g = converter_numero(request.form.get("weight_g"), float, 0.0)
        produto.length_cm = converter_numero(request.form.get("length_cm"), float, 0.0)
        produto.width_cm = converter_numero(request.form.get("width_cm"), float, 0.0)
        produto.height_cm = converter_numero(request.form.get("height_cm"), float, 0.0)
        produto.is_active = converter_numero(request.form.get("is_active"), int, 1)

        movimentacoes_pendentes = []
        for v in produto.variants:
            v_id = str(v.id)
            novo_sku = request.form.get(f"v_sku_{v_id}", v.sku).strip().upper()

            if ProductVariant.sku_existe(novo_sku, exclude_variant_id=v.id):
                flash(f"O SKU '{novo_sku}' já está cadastrado em outro produto ou variação.", "danger")
                return redirect(url_for("product.edit_product", product_id=product_id))

            v.variant_name = request.form.get(f"v_name_{v_id}", v.variant_name).strip()
            v.sku = novo_sku
            v.barcode = request.form.get(f"v_barcode_{v_id}", "").strip() or None
            v.cost_price = converter_numero(request.form.get(f"v_cost_{v_id}"), float, v.cost_price)
            v.price = converter_numero(request.form.get(f"v_price_{v_id}"), float, v.price)
            v.min_stock = converter_numero(request.form.get(f"v_min_{v_id}"), int, v.min_stock)

            novo_stock = converter_numero(request.form.get(f"v_stock_{v_id}"), int, v.stock_quantity)
            if novo_stock != v.stock_quantity:
                diferenca = novo_stock - v.stock_quantity
                tipo = "entrada" if diferenca > 0 else "saida"
                estoque_antigo = v.stock_quantity
                v.stock_quantity = novo_stock
                movimentacoes_pendentes.append({
                    "variant": v,
                    "type": tipo,
                    "qty": abs(diferenca),
                    "prev": estoque_antigo,
                    "res": novo_stock,
                    "reason": "Ajuste na tela de edição do produto"
                })

            remover_foto = request.form.get(f"v_remove_image_{v_id}") == "1"
            img_file = request.files.get(f"v_image_{v_id}")

            if img_file and img_file.filename != "":
                nova_img = salvar_imagem_produto(img_file, prefixo="var", imagem_antiga=v.image_url)
                if nova_img:
                    v.image_url = nova_img
            elif remover_foto and v.image_url:
                remover_imagem_produto(v.image_url)
                v.image_url = None

        new_row_ids = request.form.getlist("new_variant_row_id[]")
        new_names = request.form.getlist("new_variant_name[]")
        new_skus = request.form.getlist("new_variant_sku[]")
        new_barcodes = request.form.getlist("new_variant_barcode[]")
        new_costs = request.form.getlist("new_variant_cost[]")
        new_prices = request.form.getlist("new_variant_price[]")
        new_stocks = request.form.getlist("new_variant_stock[]")
        new_mins = request.form.getlist("new_variant_min_stock[]")

        novas_variantes_pendentes = []
        for i in range(len(new_skus)):
            n_sku = new_skus[i].strip().upper()
            if not n_sku:
                continue

            if ProductVariant.sku_existe(n_sku):
                flash(f"O SKU '{n_sku}' da nova variação já está em uso.", "danger")
                return redirect(url_for("product.edit_product", product_id=product_id))

            n_row_id = new_row_ids[i] if i < len(new_row_ids) else f"new_{i}"
            n_name = new_names[i].strip() if i < len(new_names) else "Variação"
            n_barcode = new_barcodes[i].strip() if i < len(new_barcodes) else ""
            n_cost = converter_numero(new_costs[i], float, 0.0) if i < len(new_costs) else 0.0
            n_price = converter_numero(new_prices[i], float, 0.0) if i < len(new_prices) else 0.0
            n_stock = converter_numero(new_stocks[i], int, 0) if i < len(new_stocks) else 0
            n_min = converter_numero(new_mins[i], int, 5) if i < len(new_mins) else 5

            n_img_file = request.files.get(f"new_variant_image_{n_row_id}")
            n_img = None
            if n_img_file and n_img_file.filename != "":
                n_img = salvar_imagem_produto(n_img_file, prefixo="var")

            novas_variantes_pendentes.append(
                ProductVariant(
                    product_id=produto.id,
                    sku=n_sku,
                    barcode=n_barcode or None,
                    variant_name=n_name,
                    cost_price=n_cost,
                    price=n_price,
                    stock_quantity=n_stock,
                    min_stock=n_min,
                    image_url=n_img
                )
            )

        try:
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                produto.salvar(cursor=cursor)

                for mov in movimentacoes_pendentes:
                    StockMovement(
                        variant_id=mov["variant"].id,
                        user_id=user_id,
                        movement_type=mov["type"],
                        quantity=mov["qty"],
                        previous_stock=mov["prev"],
                        resulting_stock=mov["res"],
                        reason=mov["reason"]
                    ).salvar(cursor=cursor)

                for nv in novas_variantes_pendentes:
                    nv.salvar(cursor=cursor)
                    if nv.stock_quantity > 0:
                        StockMovement(
                            variant_id=nv.id,
                            user_id=user_id,
                            movement_type="entrada",
                            quantity=nv.stock_quantity,
                            previous_stock=0,
                            resulting_stock=nv.stock_quantity,
                            reason="Estoque inicial da nova variação"
                        ).salvar(cursor=cursor)

            flash(f"Produto '{produto.name}' atualizado com sucesso!", "success")
            return redirect(url_for("product.list_products"))
        except Exception as e:
            flash(f"Erro ao atualizar: {e}", "danger")

    categories = Category.listar_por_loja(store_id)
    return render_template("products/form.html", product=produto, categories=categories)

@product_bp.route("/variant/<int:variant_id>/excluir", methods=["POST"])
@login_required
@role_required(["owner", "manager"])
def delete_variant(variant_id):
    store_id = session.get("store_id")
    variant = ProductVariant.buscar_por_id(variant_id, store_id)

    if not variant:
        flash("Variação não encontrada.", "danger")
        return redirect(url_for("product.list_products"))

    total_variantes = ProductVariant.contar_por_produto(variant.product_id)
    if total_variantes <= 1:
        flash("Não é possível excluir esta variação. O anúncio deve manter pelo menos uma variação ativa.", "warning")
        return redirect(url_for("product.edit_product", product_id=variant.product_id))

    sucesso = ProductVariant.excluir(variant_id, store_id)
    if sucesso:
        flash(f"Variação '{variant.variant_name}' ({variant.sku}) excluída com sucesso.", "info")
    else:
        flash("Erro ao excluir variação.", "danger")

    return redirect(url_for("product.edit_product", product_id=variant.product_id))

@product_bp.route("/<int:product_id>/excluir", methods=["POST"])
@login_required
@role_required(["owner"])
def delete_product(product_id):
    store_id = session.get("store_id")
    produto = Product.buscar_por_id(product_id, store_id)

    if produto:
        Product.excluir(product_id, store_id)
        flash(f"Produto '{produto.name}' excluído com sucesso.", "info")
    else:
        flash("Produto não encontrado.", "danger")
    return redirect(url_for("product.list_products"))

@product_bp.route("/variant/<int:variant_id>/stock", methods=["POST"])
@product_bp.route("/<int:product_id>/stock", methods=["POST"])
@login_required
def update_stock(variant_id=None, product_id=None):
    v_id = variant_id or product_id
    store_id = session.get("store_id")
    user_id = session.get("user_id")
    try:
        new_stock = converter_numero(request.form.get("stock_quantity"), int, 0)
        motivo = request.form.get("reason", "Ajuste rápido").strip()
        if new_stock < 0:
            flash("A quantidade em estoque não pode ser negativa.", "danger")
            return redirect(request.referrer or url_for("product.list_products"))
    except ValueError:
        flash("Valor numérico inválido.", "danger")
        return redirect(request.referrer or url_for("product.list_products"))

    sucesso = ProductVariant.atualizar_stock(v_id, store_id, new_stock, user_id=user_id, motivo=motivo)
    if sucesso:
        flash("Estoque atualizado com sucesso.", "success")
    else:
        flash("Variação não encontrada nesta loja.", "danger")
    return redirect(request.referrer or url_for("product.list_products"))

@product_bp.route("/movements")
@login_required
def stock_movements():
    store_id = session.get("store_id")
    pagina = max(1, request.args.get("page", 1, type=int))
    por_pagina = 20

    total_itens = StockMovement.contar_por_loja(store_id)
    total_paginas = max(1, math.ceil(total_itens / por_pagina))
    if pagina > total_paginas:
        pagina = total_paginas

    offset = (pagina - 1) * por_pagina
    movements = StockMovement.listar_por_loja(store_id, limite=por_pagina, offset=offset)

    return render_template(
        "products/movements.html",
        movements=movements,
        variant=None,
        pagina=pagina,
        total_paginas=total_paginas,
        total_itens=total_itens
    )

@product_bp.route("/variant/<int:variant_id>/history")
@login_required
def variant_history(variant_id):
    store_id = session.get("store_id")
    variant = ProductVariant.buscar_por_id(variant_id, store_id)
    if not variant:
        flash("Variação não encontrada.", "danger")
        return redirect(url_for("product.list_products"))

    movements = StockMovement.listar_por_variante(variant_id, store_id)
    return render_template(
        "products/movements.html",
        movements=movements,
        variant=variant,
        pagina=1,
        total_paginas=1,
        total_itens=len(movements)
    )

@product_bp.route("/variant/<int:variant_id>/movement", methods=["POST"])
@login_required
def create_movement(variant_id):
    store_id = session.get("store_id")
    user_id = session.get("user_id")

    tipo = request.form.get("movement_type", "entrada").strip()
    motivo = request.form.get("reason", "Entrada manual").strip()

    try:
        quantidade = converter_numero(request.form.get("quantity"), int, 0)
        if quantidade <= 0 and tipo != "ajuste":
            flash("A quantidade deve ser superior a zero para entradas ou saídas.", "danger")
            return redirect(request.referrer or url_for("product.list_products"))
        if quantidade < 0 and tipo == "ajuste":
            flash("O saldo do ajuste não pode ser negativo.", "danger")
            return redirect(request.referrer or url_for("product.list_products"))
    except ValueError:
        flash("Insira uma quantidade numérica válida.", "danger")
        return redirect(request.referrer or url_for("product.list_products"))

    sucesso = ProductVariant.registrar_movimento(
        variant_id=variant_id,
        store_id=store_id,
        user_id=user_id,
        tipo=tipo,
        quantidade=quantidade,
        motivo=motivo
    )

    if sucesso:
        flash("Movimentação de estoque cadastrada com sucesso!", "success")
    else:
        flash("Erro ao processar a movimentação.", "danger")

    return redirect(request.referrer or url_for("product.list_products"))