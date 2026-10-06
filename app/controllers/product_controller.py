from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.middlewares.auth_middleware import login_required
from app.models.product_model import Product

product_bp = Blueprint("product", __name__, url_prefix="/products")

@product_bp.route("/")
@login_required
def list_products():
    user_id = session.get("user_id")
    products = Product.listar_por_usuario(user_id)
    return render_template("products/list.html", products=products)

@product_bp.route("/novo", methods=["GET", "POST"])
@login_required
def create_product():
    if request.method == "POST":
        user_id = session.get("user_id")
        name = request.form.get("name", "").strip()
        sku = request.form.get("sku", "").strip()
        price = request.form.get("price", "0").replace(",", ".")
        stock = request.form.get("stock_quantity", "0")

        if not name or not sku:
            flash("Nome e SKU são obrigatórios.", "danger")
            return render_template("products/form.html", product=None)

        try:
            price_val = float(price)
            stock_val = int(stock)
        except ValueError:
            flash("Preço ou quantidade de stock inválidos.", "danger")
            return render_template("products/form.html", product=None)

        novo_produto = Product(
            user_id=user_id,
            name=name,
            sku=sku,
            price=price_val,
            stock_quantity=stock_val
        )
        novo_produto.salvar()

        flash(f"Produto '{name}' registado com sucesso!", "success")
        return redirect(url_for("product.list_products"))

    return render_template("products/form.html", product=None)

@product_bp.route("/<int:product_id>/editar", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    user_id = session.get("user_id")
    product = Product.buscar_por_id(product_id, user_id)

    if not product:
        flash("Produto não encontrado.", "danger")
        return redirect(url_for("product.list_products"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        sku = request.form.get("sku", "").strip()
        price = request.form.get("price", "0").replace(",", ".")
        stock = request.form.get("stock_quantity", "0")

        if not name or not sku:
            flash("Nome e SKU são obrigatórios.", "danger")
            return render_template("products/form.html", product=product)

        try:
            product.name = name
            product.sku = sku
            product.price = float(price)
            product.stock_quantity = int(stock)
            product.salvar()

            flash(f"Produto '{name}' atualizado com sucesso!", "success")
            return redirect(url_for("product.list_products"))
        except ValueError:
            flash("Preço ou quantidade de stock inválidos.", "danger")

    return render_template("products/form.html", product=product)

@product_bp.route("/<int:product_id>/excluir", methods=["POST"])
@login_required
def delete_product(product_id):
    user_id = session.get("user_id")
    product = Product.buscar_por_id(product_id, user_id)

    if product:
        Product.excluir(product_id, user_id)
        flash(f"Produto '{product.name}' removido com sucesso.", "info")
    else:
        flash("Produto não encontrado.", "danger")

    return redirect(url_for("product.list_products"))

@product_bp.route("/<int:product_id>/estoque", methods=["POST"])
@login_required
def update_stock(product_id):
    user_id = session.get("user_id")
    novo_estoque = request.form.get("stock_quantity")

    try:
        qtd = int(novo_estoque)
        if qtd < 0:
            raise ValueError
        Product.atualizar_estoque(product_id, user_id, qtd)
        flash("Stock atualizado com sucesso!", "success")
    except (ValueError, TypeError):
        flash("Quantidade de stock inválida.", "danger")

    return redirect(url_for("product.list_products"))