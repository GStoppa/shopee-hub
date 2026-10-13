from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.middlewares.auth_middleware import login_required, role_required
from app.models.category_model import Category

category_bp = Blueprint("category", __name__, url_prefix="/categories")

@category_bp.route("/", methods=["GET"])
@login_required
def list_categories():
    store_id = session.get("store_id")
    categories = Category.listar_por_loja(store_id)
    return render_template("categories/index.html", categories=categories)

@category_bp.route("/novo", methods=["POST"])
@login_required
@role_required(["owner", "manager"])
def create_category():
    store_id = session.get("store_id")
    name = request.form.get("name", "").strip()

    if not name:
        flash("O nome da categoria é obrigatório.", "danger")
        return redirect(url_for("category.list_categories"))

    Category(store_id=store_id, name=name).salvar()
    flash(f"Categoria '{name}' criada com sucesso!", "success")
    return redirect(url_for("category.list_categories"))

@category_bp.route("/<int:category_id>/editar", methods=["POST"])
@login_required
@role_required(["owner", "manager"])
def edit_category(category_id):
    store_id = session.get("store_id")
    category = Category.buscar_por_id(category_id, store_id)

    if not category:
        flash("Categoria não encontrada.", "danger")
        return redirect(url_for("category.list_categories"))

    name = request.form.get("name", "").strip()
    if not name:
        flash("O nome da categoria não pode ficar vazio.", "danger")
        return redirect(url_for("category.list_categories"))

    category.name = name
    category.salvar()
    flash("Categoria atualizada com sucesso!", "success")
    return redirect(url_for("category.list_categories"))

@category_bp.route("/<int:category_id>/excluir", methods=["POST"])
@login_required
@role_required(["owner", "manager"])
def delete_category(category_id):
    store_id = session.get("store_id")
    category = Category.buscar_por_id(category_id, store_id)

    if not category:
        flash("Categoria não encontrada.", "danger")
        return redirect(url_for("category.list_categories"))

    Category.excluir(category_id, store_id)
    flash(f"Categoria '{category.name}' removida com sucesso.", "info")
    return redirect(url_for("category.list_categories"))