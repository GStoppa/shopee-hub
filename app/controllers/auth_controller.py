from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.database import DatabaseConnection
from app.models.user_model import User
from app.models.store_model import Store

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

def validar_email(email: str) -> bool:
    return bool(email and "@" in email and "." in email.split("@")[-1])

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("main.welcome"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")

        if not email or not password:
            flash("Informe o e-mail e a senha de acesso.", "danger")
            return render_template("auth/login.html")

        user = User.buscar_por_email(email)
        if user and user.check_password(password):
            session.clear()
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_role"] = user.role
            session["store_id"] = user.store_id

            store = Store.buscar_por_id(user.store_id)
            session["store_name"] = store.name if store else "Minha Loja"

            flash(f"Bem-vindo(a) de volta, {user.name}!", "success")
            return redirect(url_for("main.welcome"))

        flash("E-mail ou senha incorretos.", "danger")

    return render_template("auth/login.html")

@auth_bp.route("/cadastro", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("main.welcome"))

    if request.method == "POST":
        store_name = request.form.get("store_name", "").strip()
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not store_name or not name or not email or not password or not confirm_password:
            flash("Todos os campos são obrigatórios.", "danger")
            return render_template("auth/register.html")

        if not validar_email(email):
            flash("Insira um endereço de e-mail válido (ex: seu.nome@dominio.com).", "danger")
            return render_template("auth/register.html")

        if password != confirm_password:
            flash("A confirmação de senha não confere com a nova senha digitada.", "danger")
            return render_template("auth/register.html")

        if len(password) < 6:
            flash("A senha deve conter no mínimo 6 caracteres.", "danger")
            return render_template("auth/register.html")

        if User.buscar_por_email(email):
            flash("Este e-mail já está em uso por outro usuário.", "danger")
            return render_template("auth/register.html")

        # Transação atômica única: Loja e Usuário criados juntos
        try:
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                nova_loja = Store(name=store_name).salvar(cursor=cursor)
                novo_usuario = User(
                    name=name,
                    email=email,
                    store_id=nova_loja.id,
                    role="owner"
                )
                novo_usuario.set_password(password)
                novo_usuario.salvar(cursor=cursor)

            flash("Conta e loja criadas com sucesso! Faça login para iniciar.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            flash(f"Erro ao processar o cadastro: {e}", "danger")
            return render_template("auth/register.html")

    return render_template("auth/register.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Sessão encerrada com sucesso.", "info")
    return redirect(url_for("auth.login"))