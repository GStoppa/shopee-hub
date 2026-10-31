from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.middlewares.auth_middleware import login_required
from app.models.user_model import User

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")

@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    user_id = session.get("user_id")
    user = User.buscar_por_id(user_id)

    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_info":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()

            if not name or not email:
                flash("Nome e e-mail são obrigatórios.", "danger")
                return redirect(url_for("profile.index"))

            if "@" not in email or "." not in email.split("@")[-1]:
                flash("Insira um endereço de e-mail válido.", "danger")
                return redirect(url_for("profile.index"))
            
            existente = User.buscar_por_email(email)
            if existente and existente.id != user.id:
                flash("Este e-mail já está sendo utilizado por outro usuário.", "danger")
                return redirect(url_for("profile.index"))

            user.name = name
            user.email = email
            user.salvar()

            session["user_name"] = user.name
            flash("Dados do perfil atualizados com sucesso!", "success")

        elif action == "update_password":
            current_password = request.form.get("current_password")
            new_password = request.form.get("new_password")
            confirm_password = request.form.get("confirm_password")

            if not current_password or not new_password or not confirm_password:
                flash("Preencha todos os campos para alterar a senha.", "danger")
                return redirect(url_for("profile.index"))

            if not user.check_password(current_password):
                flash("A senha atual digitada está incorreta.", "danger")
                return redirect(url_for("profile.index"))

            if new_password != confirm_password:
                flash("A nova senha e a confirmação não conferem.", "danger")
                return redirect(url_for("profile.index"))

            if len(new_password) < 6:
                flash("A nova senha deve ter no mínimo 6 caracteres.", "danger")
                return redirect(url_for("profile.index"))

            user.set_password(new_password)
            user.salvar()
            flash("Senha alterada com sucesso!", "success")

        return redirect(url_for("profile.index"))

    return render_template("profile/index.html", user=user)