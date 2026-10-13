from flask import Blueprint, render_template, session
from app.middlewares.auth_middleware import login_required
from app.models.product_model import Product

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
@main_bp.route("/welcome")
@login_required
def welcome():
    store_id = session.get("store_id")

    metricas = Product.obter_metricas_dashboard(store_id)
    produtos_criticos = Product.listar_produtos_criticos(store_id, limite=6)

    return render_template(
        "main/welcome.html",
        metricas=metricas,
        produtos_criticos=produtos_criticos
    )