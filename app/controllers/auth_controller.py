from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.user_model import User
from app.models.store_model import Store
from app.database import DatabaseConnection
import re

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

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
            session["store_logo"] = store.logo_url if store else None

            flash(f"Bem-vindo de volta, {user.name}!", "success")
            return redirect(url_for("main.welcome"))

        flash("E-mail ou palavra-passe inválidos.", "danger")

    return render_template("auth/login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("main.welcome"))

    if request.method == "POST":
        # 1. Dados da Loja
        store_name = request.form.get("store_name", "").strip()
        document = request.form.get("document", "").strip()
        phone = request.form.get("phone", "").strip()

        # 2. Dados do Dono da Conta
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        form_data = {
            "store_name": store_name,
            "document": document,
            "phone": phone,
            "name": name,
            "email": email
        }

        if not re.match(EMAIL_REGEX, email):
            flash("O endereço de e-mail fornecido não tem um formato válido.", "danger")
            return render_template("auth/register.html", form_data=form_data)
        
        if not store_name or not name or not email or not password:
            flash("Preencha todos os campos obrigatórios (Nome da Loja, Seu Nome, E-mail e Senha).", "danger")
            return render_template("auth/register.html", form_data=form_data)

        if len(password) < 6:
            flash("A palavra-passe deve conter pelo menos 6 carateres.", "warning")
            return render_template("auth/register.html", form_data=form_data)

        if password != confirm_password:
            flash("As palavras-passe não coincidem.", "danger")
            return render_template("auth/register.html", form_data=form_data)

        if User.buscar_por_email(email):
            flash("Este e-mail já se encontra registado. Tente iniciar sessão.", "warning")
            return render_template("auth/register.html", form_data=form_data)

        # Transação Atómica: Criação da Loja e do Dono na mesma conexão
        try:
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

                # Inserção da Loja
                cursor.execute("""
                    INSERT INTO stores (name, document, phone, created_at)
                    VALUES (?, ?, ?, ?)
                """, (store_name, document or None, phone or None, now))
                store_id = cursor.lastrowid

                # Inserção do Utilizador Administrador (Role: 'owner')
                pwd_hash = generate_password_hash(password)
                cursor.execute("""
                    INSERT INTO users (store_id, name, email, password_hash, role, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (store_id, name, email, pwd_hash, "owner", now))

            flash("Registo concluído com sucesso! Inicie sessão para começar a gerir a sua loja.", "success")
            return redirect(url_for("auth.login"))

        except Exception as e:
            flash("Ocorreu um erro ao registar a sua conta. Por favor, tente novamente.", "danger")
            return render_template("auth/register.html", form_data=form_data)

    return render_template("auth/register.html", form_data={})

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Sessão terminada com sucesso.", "info")
    return redirect(url_for("auth.login"))