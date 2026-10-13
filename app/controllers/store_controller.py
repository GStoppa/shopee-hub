from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.middlewares.auth_middleware import login_required, role_required
from app.models.store_model import Store
from app.utils.upload import salvar_logo_loja

store_bp = Blueprint("store", __name__, url_prefix="/store")

@store_bp.route("/settings", methods=["GET", "POST"])
@login_required
@role_required(["owner", "manager"])
def settings():
    store_id = session.get("store_id")
    store = Store.buscar_por_id(store_id)

    if not store:
        flash("Loja não encontrada.", "danger")
        return redirect(url_for("main.welcome"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        document = request.form.get("document", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        shopee_shop_id = request.form.get("shopee_shop_id", "").strip()
        logo_file = request.files.get("logo")

        if not name:
            flash("O nome da loja é obrigatório.", "danger")
            return render_template("store/settings.html", store=store)

        try:
            if logo_file and logo_file.filename != "":
                caminho_logo = salvar_logo_loja(logo_file, store.id, logo_antigo=store.logo_url)
                if caminho_logo:
                    store.logo_url = caminho_logo
        except ValueError as err:
            flash(str(err), "danger")
            return render_template("store/settings.html", store=store)

        store.name = name
        store.document = document
        store.phone = phone
        store.address = address
        store.shopee_shop_id = shopee_shop_id
        store.salvar()

        session["store_name"] = store.name
        session["store_logo"] = store.logo_url

        flash("Definições da loja atualizadas com sucesso!", "success")
        return redirect(url_for("store.settings"))

    return render_template("store/settings.html", store=store)