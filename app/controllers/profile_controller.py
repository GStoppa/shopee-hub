from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.middlewares.auth_middleware import login_required
from app.models.user_model import User
from app.models.store_model import Store

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")

@profile_bp.route("/", methods=["GET"])
@login_required
def index():
    user = User.buscar_por_id(session.get("user_id"))
    if not user:
        flash("Utilizador não encontrado.", "danger")
        return redirect(url_for("auth.logout"))

    store = Store.buscar_por_id(user.store_id) if user.store_id else None
    return render_template("profile/index.html", user=user, store=store)

@profile_bp.route("/dados", methods=["POST"])
@login_required
def update_info():
    user = User.buscar_por_id(session.get("user_id"))
    if not user:
        return redirect(url_for("auth.logout"))

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()

    if not name or not email:
        flash("Nome e e-mail são obrigatórios.", "danger")
        return redirect(url_for("profile.index"))

    if email != user.email:
        usuario_existente = User.buscar_por_email(email)
        if usuario_existente and usuario_existente.id != user.id:
            flash("Este e-mail já se encontra registado por outro utilizador.", "warning")
            return redirect(url_for("profile.index"))

    user.name = name
    user.email = email
    user.salvar()

    session["user_name"] = user.name
    session["user_email"] = user.email

    flash("Dados pessoais atualizados com sucesso!", "success")
    return redirect(url_for("profile.index"))

@profile_bp.route("/senha", methods=["POST"])
@login_required
def update_password():
    user = User.buscar_por_id(session.get("user_id"))
    if not user:
        return redirect(url_for("auth.logout"))

    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not user.check_password(current_password):
        flash("A palavra-passe atual está incorreta.", "danger")
        return redirect(url_for("profile.index"))

    if len(new_password) < 6:
        flash("A nova palavra-passe deve conter pelo menos 6 carateres.", "warning")
        return redirect(url_for("profile.index"))

    if new_password != confirm_password:
        flash("A confirmação da nova palavra-passe não coincide.", "danger")
        return redirect(url_for("profile.index"))

    user.set_password(new_password)
    user.salvar()

    flash("Palavra-passe alterada com sucesso!", "success")
    return redirect(url_for("profile.index"))