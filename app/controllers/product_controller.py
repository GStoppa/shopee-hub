from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.middlewares.auth_middleware import login_required, role_required
from app.models.product_model import Product, ProductVariant, StockMovement
from app.models.category_model import Category
from app.utils.upload import salvar_imagem_produto

product_bp = Blueprint("product", __name__, url_prefix="/products")

def converter_moeda(valor_str: str) -> float:
    if not valor_str:
        return 0.0
    limpo = str(valor_str).strip().replace("R$", "").replace(" ", "").replace(",", ".")
    try:
        val = float(limpo)
        return max(val, 0.0)
    except ValueError:
        return 0.0

@product_bp.route("/")
@login_required
def list_products():
    store_id = session.get("store_id")
    busca = request.args.get("q", "").strip()
    cat_id = request.args.get("category_id", type=int)
    status = request.args.get("status", "").strip()

    products = Product.listar_por_loja(store_id, busca=busca, category_id=cat_id, status=status)
    categories = Category.listar_por_loja(store_id)
    return render_template("products/list.html", products=products, categories=categories)

@product_bp.route("/movements")
@login_required
def stock_movements():
    store_id = session.get("store_id")
    movements = StockMovement.listar_por_loja(store_id, limite=100)
    return render_template("products/movements.html", movements=movements, variant=None)

@product_bp.route("/variant/<int:variant_id>/history")
@login_required
def variant_history(variant_id):
    store_id = session.get("store_id")
    variant = ProductVariant.buscar_por_id(variant_id, store_id)
    if not variant:
        flash("Variação não encontrada.", "danger")
        return redirect(url_for("product.list_products"))

    movements = StockMovement.listar_por_variante(variant_id, store_id)
    return render_template("products/movements.html", movements=movements, variant=variant)

@product_bp.route("/variant/<int:variant_id>/movement", methods=["POST"])
@login_required
def create_movement(variant_id):
    store_id = session.get("store_id")
    user_id = session.get("user_id")

    tipo = request.form.get("movement_type", "entrada").strip()
    motivo = request.form.get("reason", "Entrada manual").strip()

    try:
        quantidade = int(request.form.get("quantity", 0))
        if quantidade <= 0 and tipo != "ajuste":
            flash("A quantidade deve ser superior a zero.", "danger")
            return redirect(request.referrer or url_for("product.list_products"))
        if quantidade < 0 and tipo == "ajuste":
            flash("O saldo do ajuste não pode ser negativo.", "danger")
            return redirect(request.referrer or url_for("product.list_products"))
    except ValueError:
        flash("Introduza uma quantidade numérica válida.", "danger")
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
        flash("Movimentação de stock registada com sucesso!", "success")
    else:
        flash("Erro ao processar a movimentação.", "danger")

    return redirect(request.referrer or url_for("product.list_products"))

@product_bp.route("/novo", methods=["GET", "POST"])
@login_required
@role_required(["owner", "manager"])
def create_product():
    store_id = session.get("store_id")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category_id = request.form.get("category_id") or None
        description = request.form.get("description", "").strip()
        weight_g = float(request.form.get("weight_g") or 0.0)
        length_cm = float(request.form.get("length_cm") or 0.0)
        width_cm = float(request.form.get("width_cm") or 0.0)
        height_cm = float(request.form.get("height_cm") or 0.0)
        is_active = int(request.form.get("is_active", 1))

        has_variants = request.form.get("has_variants") == "1"

        if not name:
            flash("O nome do produto é obrigatório.", "danger")
            categories = Category.listar_por_loja(store_id)
            return render_template("products/form.html", product=None, categories=categories)

        variantes = []

        if not has_variants:
            sku = request.form.get("simple_sku", "").strip().upper()
            barcode = request.form.get("simple_barcode", "").strip()
            price = converter_moeda(request.form.get("simple_price", "0"))
            cost_price = converter_moeda(request.form.get("simple_cost_price", "0"))
            stock_quantity = int(request.form.get("simple_stock", 0))
            min_stock = int(request.form.get("simple_min_stock", 5))

            if not sku:
                flash("O SKU é obrigatório para o produto simples.", "danger")
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
            v_names = request.form.getlist("variant_name[]")
            v_skus = request.form.getlist("variant_sku[]")
            v_barcodes = request.form.getlist("variant_barcode[]")
            v_costs = request.form.getlist("variant_cost[]")
            v_prices = request.form.getlist("variant_price[]")
            v_stocks = request.form.getlist("variant_stock[]")
            v_min_stocks = request.form.getlist("variant_min_stock[]")
            v_images = request.files.getlist("variant_image[]")

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
                    flash(f"SKU duplicado dentro das variações: {sku}", "danger")
                    categories = Category.listar_por_loja(store_id)
                    return render_template("products/form.html", product=None, categories=categories)
                skus_vistos.add(sku)

                v_name = v_names[i].strip() if i < len(v_names) else "Variação"
                v_barcode = v_barcodes[i].strip() if i < len(v_barcodes) else ""
                v_cost = converter_moeda(v_costs[i]) if i < len(v_costs) else 0.0
                v_price = converter_moeda(v_prices[i]) if i < len(v_prices) else 0.0
                v_stock = int(v_stocks[i]) if i < len(v_stocks) and v_stocks[i] else 0
                v_min = int(v_min_stocks[i]) if i < len(v_min_stocks) and v_min_stocks[i] else 5

                img_url = None
                if i < len(v_images) and v_images[i] and v_images[i].filename != "":
                    img_url = salvar_imagem_produto(v_images[i], prefixo="var")

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
            produto.salvar()
            flash(f"Produto '{name}' registado com sucesso!", "success")
            return redirect(url_for("product.list_products"))
        except Exception as e:
            flash(f"Erro ao registar o produto (verifique se os SKUs já existem): {e}", "danger")

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
        produto.name = request.form.get("name", "").strip()
        produto.category_id = request.form.get("category_id") or None
        produto.description = request.form.get("description", "").strip()
        produto.weight_g = float(request.form.get("weight_g") or 0.0)
        produto.length_cm = float(request.form.get("length_cm") or 0.0)
        produto.width_cm = float(request.form.get("width_cm") or 0.0)
        produto.height_cm = float(request.form.get("height_cm") or 0.0)
        produto.is_active = int(request.form.get("is_active", 1))

        for v in produto.variants:
            v_id = str(v.id)
            v.variant_name = request.form.get(f"v_name_{v_id}", v.variant_name).strip()
            v.sku = request.form.get(f"v_sku_{v_id}", v.sku).strip().upper()
            v.barcode = request.form.get(f"v_barcode_{v_id}", "").strip() or None
            v.cost_price = converter_moeda(request.form.get(f"v_cost_{v_id}", str(v.cost_price)))
            v.price = converter_moeda(request.form.get(f"v_price_{v_id}", str(v.price)))
            v.min_stock = int(request.form.get(f"v_min_{v_id}", v.min_stock))

            img_file = request.files.get(f"v_image_{v_id}")
            if img_file and img_file.filename != "":
                nova_img = salvar_imagem_produto(img_file, prefixo="var", imagem_antiga=v.image_url)
                if nova_img:
                    v.image_url = nova_img

        try:
            produto.salvar()
            flash(f"Produto '{produto.name}' atualizado com sucesso!", "success")
            return redirect(url_for("product.list_products"))
        except Exception as e:
            flash(f"Erro ao atualizar: {e}", "danger")

    categories = Category.listar_por_loja(store_id)
    return render_template("products/form.html", product=produto, categories=categories)

@product_bp.route("/<int:product_id>/excluir", methods=["POST"])
@login_required
@role_required(["owner"])
def delete_product(product_id):
    store_id = session.get("store_id")
    produto = Product.buscar_por_id(product_id, store_id)

    if produto:
        Product.excluir(product_id, store_id)
        flash(f"Produto '{produto.name}' removido.", "info")
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
        new_stock = int(request.form.get("stock_quantity", 0))
        motivo = request.form.get("reason", "Ajuste manual").strip()
        if new_stock < 0:
            flash("A quantidade em stock não pode ser negativa.", "danger")
            return redirect(request.referrer or url_for("product.list_products"))
    except ValueError:
        flash("Valor numérico inválido.", "danger")
        return redirect(request.referrer or url_for("product.list_products"))

    sucesso = ProductVariant.atualizar_stock(v_id, store_id, new_stock, user_id=user_id, motivo=motivo)
    if sucesso:
        flash("Stock atualizado com sucesso.", "success")
    else:
        flash("Variação não encontrada nesta loja.", "danger")
    return redirect(request.referrer or url_for("product.list_products"))