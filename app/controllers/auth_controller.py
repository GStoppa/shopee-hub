from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.user_model import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("main.welcome"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = User.buscar_por_email(email)

        if user and user.check_password(password):
            session.clear()
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_email"] = user.email
            flash(f"Bem-vindo de volta, {user.name}!", "success")
            return redirect(url_for("main.welcome"))

        flash("E-mail ou senha inválidos.", "danger")

    return render_template("auth/login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("main.welcome"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("Todos os campos são obrigatórios.", "danger")
            return render_template("auth/register.html")

        if len(password) < 6:
            flash("A senha deve conter no mínimo 6 caracteres.", "warning")
            return render_template("auth/register.html")

        if password != confirm_password:
            flash("As senhas não coincidem.", "danger")
            return render_template("auth/register.html")

        if User.buscar_por_email(email):
            flash("Este e-mail já está cadastrado.", "warning")
            return render_template("auth/register.html")

        novo_usuario = User(name=name, email=email)
        novo_usuario.set_password(password)
        novo_usuario.salvar()

        flash("Cadastro realizado com sucesso! Faça login para continuar.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Sessão encerrada com sucesso.", "info")
    return redirect(url_for("auth.login"))