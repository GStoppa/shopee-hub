from flask import Blueprint, render_template, session
from app.middlewares.auth_middleware import login_required
from app.models.product_model import Product

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
@login_required
def welcome():
    store_id = session.get("store_id")
    metricas = Product.obter_metricas_dashboard(store_id)
    produtos_criticos = Product.listar_produtos_criticos(store_id)

    margem_geral = 0.0
    if metricas["valor_estoque"] > 0:
        margem_geral = round(
            ((metricas["valor_estoque"] - metricas["custo_estoque"]) / metricas["valor_estoque"]) * 100, 
            2
        )

    margem_negativa = margem_geral <= 0

    return render_template(
        "main/welcome.html",
        metricas=metricas,
        produtos_criticos=produtos_criticos,
        margem_geral=margem_geral,
        margem_negativa=margem_negativa
    )