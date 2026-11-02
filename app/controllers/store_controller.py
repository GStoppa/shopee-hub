from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.middlewares.auth_middleware import login_required, role_required
from app.models.store_model import Store
from app.utils.upload import salvar_logo_loja, remover_imagem_produto

store_bp = Blueprint("store", __name__, url_prefix="/store")

@store_bp.route("/settings", methods=["GET", "POST"])
@login_required
@role_required(["owner"])
def settings():
    store_id = session.get("store_id")
    store = Store.buscar_por_id(store_id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        document = request.form.get("document", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        shopee_shop_id = request.form.get("shopee_shop_id", "").strip()

        if not name:
            flash("O nome da loja é obrigatório.", "danger")
            return render_template("store/settings.html", store=store)

        logo_file = request.files.get("logo")
        logo_url = store.logo_url if store else None
        logo_antigo_para_remover = None
        novo_logo_salvo = None

        if logo_file and logo_file.filename != "":
            try:
                novo_logo_salvo = salvar_logo_loja(logo_file)
                if novo_logo_salvo:
                    if store and store.logo_url:
                        logo_antigo_para_remover = store.logo_url
                    logo_url = novo_logo_salvo
            except ValueError as ve:
                flash(str(ve), "danger")
                return render_template("store/settings.html", store=store)

        try:
            if store:
                store.name = name
                store.document = document
                store.phone = phone
                store.address = address
                store.shopee_shop_id = shopee_shop_id
                store.logo_url = logo_url
                store.salvar()
            else:
                store = Store(
                    name=name,
                    document=document,
                    phone=phone,
                    address=address,
                    shopee_shop_id=shopee_shop_id,
                    logo_url=logo_url
                ).salvar()

            if logo_antigo_para_remover:
                remover_imagem_produto(logo_antigo_para_remover)

            session["store_name"] = store.name
            session["store_logo_url"] = store.logo_url if store.logo_url else None

            flash("Configurações da loja guardadas com sucesso!", "success")
            return redirect(url_for("store.settings"))
        except Exception as e:
            if novo_logo_salvo:
                remover_imagem_produto(novo_logo_salvo)
            flash(f"Erro ao guardar configurações da loja: {e}", "danger")

    return render_template("store/settings.html", store=store)