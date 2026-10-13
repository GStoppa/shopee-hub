import re
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.middlewares.auth_middleware import login_required
from app.models.user_model import User

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

@profile_bp.route("/", methods=["GET"])
@login_required
def index():
    user_id = session.get("user_id")
    user = User.buscar_por_id(user_id)

    if not user:
        flash("Utilizador não encontrado.", "danger")
        return redirect(url_for("auth.login"))

    return render_template("profile/index.html", user=user)

@profile_bp.route("/update-info", methods=["POST"])
@login_required
def update_info():
    user_id = session.get("user_id")
    user = User.buscar_por_id(user_id)

    if not user:
        flash("Utilizador não encontrado.", "danger")
        return redirect(url_for("auth.login"))

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()

    if not name or not email:
        flash("Nome e e-mail não podem ficar em branco.", "danger")
        return redirect(url_for("profile.index"))

    if not re.match(EMAIL_REGEX, email):
        flash("Formato de e-mail inválido.", "danger")
        return redirect(url_for("profile.index"))

    # Verifica se o e-mail já pertence a outro utilizador
    existente = User.buscar_por_email(email)
    if existente and existente.id != user.id:
        flash("Este endereço de e-mail já está associado a outra conta.", "danger")
        return redirect(url_for("profile.index"))

    user.name = name
    user.email = email
    user.salvar()

    # Sincronização em tempo real dos dados na sessão
    session["user_name"] = user.name
    session["user_email"] = user.email

    flash("Dados pessoais atualizados com sucesso!", "success")
    return redirect(url_for("profile.index"))

@profile_bp.route("/update-password", methods=["POST"])
@login_required
def update_password():
    user_id = session.get("user_id")
    user = User.buscar_por_id(user_id)

    if not user:
        flash("Utilizador não encontrado.", "danger")
        return redirect(url_for("auth.login"))

    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()

    if not current_password or not new_password:
        flash("Preencha a palavra-passe atual e a nova palavra-passe.", "danger")
        return redirect(url_for("profile.index"))

    if not user.check_password(current_password):
        flash("A palavra-passe atual está incorreta.", "danger")
        return redirect(url_for("profile.index"))

    if len(new_password) < 6:
        flash("A nova palavra-passe deve conter pelo menos 6 carateres.", "warning")
        return redirect(url_for("profile.index"))

    if confirm_password and new_password != confirm_password:
        flash("A confirmação da palavra-passe não coincide.", "danger")
        return redirect(url_for("profile.index"))

    user.set_password(new_password)
    user.salvar()

    flash("Palavra-passe alterada com sucesso!", "success")
    return redirect(url_for("profile.index"))