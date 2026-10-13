import re
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.middlewares.auth_middleware import login_required
from app.models.user_model import User

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    user_id = session.get("user_id")
    user = User.buscar_por_id(user_id)

    if not user:
        flash("Utilizador não encontrado.", "danger")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "").strip()

        if not name or not email:
            flash("Nome e e-mail não podem ficar em branco.", "danger")
            return render_template("profile/index.html", user=user)

        if not re.match(EMAIL_REGEX, email):
            flash("Formato de e-mail inválido.", "danger")
            return render_template("profile/index.html", user=user)

        existente = User.buscar_por_email(email)
        if existente and existente.id != user.id:
            flash("Este endereço de e-mail já pertence a outra conta.", "danger")
            return render_template("profile/index.html", user=user)

        if new_password:
            if not current_password or not user.check_password(current_password):
                flash("A palavra-passe atual está incorreta.", "danger")
                return render_template("profile/index.html", user=user)
            if len(new_password) < 6:
                flash("A nova palavra-passe deve conter no mínimo 6 carateres.", "warning")
                return render_template("profile/index.html", user=user)
            user.set_password(new_password)

        user.name = name
        user.email = email
        user.salvar()

        # Atualização imediata dos dados em sessão
        session["user_name"] = user.name
        session["user_email"] = user.email

        flash("Perfil atualizado com sucesso!", "success")
        return redirect(url_for("profile.index"))

    return render_template("profile/index.html", user=user)