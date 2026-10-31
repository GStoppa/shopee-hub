from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.middlewares.auth_middleware import login_required, role_required
from app.models.category_model import Category

category_bp = Blueprint("category", __name__, url_prefix="/categories")

@category_bp.route("/")
@login_required
def list_categories():
    store_id = session.get("store_id")
    categories = Category.listar_por_loja(store_id)
    return render_template("categories/index.html", categories=categories, category_to_edit=None)

@category_bp.route("/novo", methods=["POST"])
@login_required
@role_required(["owner", "manager"])
def create_category():
    store_id = session.get("store_id")
    name = request.form.get("name", "").strip()

    if not name:
        flash("O nome da categoria é obrigatório.", "danger")
        return redirect(url_for("category.list_categories"))

    if Category.nome_existe(name, store_id):
        flash(f"A categoria '{name}' já existe nesta loja.", "warning")
        return redirect(url_for("category.list_categories"))

    Category(store_id=store_id, name=name).salvar()
    flash(f"Categoria '{name}' cadastrada com sucesso!", "success")
    return redirect(url_for("category.list_categories"))

@category_bp.route("/<int:category_id>/editar", methods=["GET", "POST"])
@login_required
@role_required(["owner", "manager"])
def edit_category(category_id):
    store_id = session.get("store_id")
    categoria = Category.buscar_por_id(category_id, store_id)

    if not categoria:
        flash("Categoria não encontrada.", "danger")
        return redirect(url_for("category.list_categories"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()

        if not name:
            flash("O nome da categoria não pode ficar em branco.", "danger")
            return redirect(url_for("category.edit_category", category_id=category_id))

        if Category.nome_existe(name, store_id, exclude_id=category_id):
            flash(f"Já existe outra categoria chamada '{name}' nesta loja.", "warning")
            return redirect(url_for("category.edit_category", category_id=category_id))

        categoria.name = name
        categoria.salvar()

        flash(f"Categoria '{name}' atualizada com sucesso!", "success")
        return redirect(url_for("category.list_categories"))

    categories = Category.listar_por_loja(store_id)
    return render_template("categories/index.html", categories=categories, category_to_edit=categoria)

@category_bp.route("/<int:category_id>/excluir", methods=["POST"])
@login_required
@role_required(["owner", "manager"])
def delete_category(category_id):
    store_id = session.get("store_id")
    sucesso = Category.excluir(category_id, store_id)
    if sucesso:
        flash("Categoria excluída com sucesso.", "info")
    else:
        flash("Categoria não encontrada.", "danger")
    return redirect(url_for("category.list_categories"))