from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.user_model import User
from app.models.store_model import Store

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("main.welcome"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.buscar_por_email(email)

        if user and user.check_password(password):
            session.clear()
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_email"] = user.email
            session["store_id"] = user.store_id
            session["user_role"] = user.role

            store = Store.buscar_por_id(user.store_id) if user.store_id else None
            session["store_name"] = store.name if store else "Minha Loja"

            flash(f"Bem-vindo de volta, {user.name}!", "success")
            return redirect(url_for("main.welcome"))

        flash("E-mail ou palavra-passe inválidos.", "danger")

    return render_template("auth/login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("main.welcome"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("Todos os campos são obrigatórios.", "danger")
            return render_template("auth/register.html")

        if len(password) < 6:
            flash("A palavra-passe deve conter no mínimo 6 caracteres.", "warning")
            return render_template("auth/register.html")

        if password != confirm_password:
            flash("As palavras-passe não coincidem.", "danger")
            return render_template("auth/register.html")

        if User.buscar_por_email(email):
            flash("Este e-mail já está registado.", "warning")
            return render_template("auth/register.html")

        # Cria uma loja dedicada para este utilizador e define-o como 'owner'
        nova_loja = Store(name=f"Loja de {name}").salvar()

        novo_usuario = User(
            name=name, 
            email=email, 
            store_id=nova_loja.id, 
            role="owner"
        )
        novo_usuario.set_password(password)
        novo_usuario.salvar()

        flash("Registo concluído! Inicie sessão para aceder ao painel.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Sessão terminada com sucesso.", "info")
    return redirect(url_for("auth.login"))