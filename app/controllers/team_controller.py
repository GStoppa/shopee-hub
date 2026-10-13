import re
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.middlewares.auth_middleware import login_required, role_required
from app.models.user_model import User

team_bp = Blueprint("team", __name__, url_prefix="/team")
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

@team_bp.route("/")
@login_required
@role_required(["owner", "manager"])
def list_members():
    store_id = session.get("store_id")
    members = User.listar_por_loja(store_id)
    return render_template("team/list.html", members=members)

@team_bp.route("/novo", methods=["GET", "POST"])
@login_required
@role_required(["owner", "manager"])
def create_member():
    store_id = session.get("store_id")
    current_role = session.get("user_role")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "operator")

        if current_role == "manager" and role != "operator":
            flash("Gerentes apenas têm autorização para registar operadores.", "danger")
            return render_template("team/form.html")

        if not name or not email or not password:
            flash("Preencha todos os campos obrigatórios.", "danger")
            return render_template("team/form.html")

        if not re.match(EMAIL_REGEX, email):
            flash("Formato de e-mail inválido.", "danger")
            return render_template("team/form.html")

        if len(password) < 6:
            flash("A palavra-passe deve ter pelo menos 6 carateres.", "warning")
            return render_template("team/form.html")

        if User.buscar_por_email(email):
            flash("Este endereço de e-mail já está a ser utilizado.", "warning")
            return render_template("team/form.html")

        novo_membro = User(
            name=name,
            email=email,
            store_id=store_id,
            role=role
        )
        novo_membro.set_password(password)
        novo_membro.salvar()

        flash(f"Colaborador '{name}' adicionado com sucesso!", "success")
        return redirect(url_for("team.list_members"))

    return render_template("team/form.html")

@team_bp.route("/<int:member_id>/editar", methods=["GET", "POST"])
@login_required
@role_required(["owner", "manager"])
def edit_member(member_id):
    store_id = session.get("store_id")
    current_user_id = session.get("user_id")
    current_role = session.get("user_role")

    member = User.buscar_por_id(member_id)

    if not member or member.store_id != store_id:
        flash("Colaborador não encontrado.", "danger")
        return redirect(url_for("team.list_members"))

    if current_role == "manager" and member.role != "operator":
        flash("Não tem permissão para editar este colaborador.", "danger")
        return redirect(url_for("team.list_members"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role", member.role)
        new_password = request.form.get("password", "").strip()

        if current_role == "manager" and role != "operator":
            flash("Não possui autorização para alterar o cargo para além de operador.", "danger")
            return render_template("team/edit.html", member=member)

        if member.id == current_user_id and member.role == "owner" and role != "owner":
            todos = User.listar_por_loja(store_id)
            outros_donos = [m for m in todos if m.role == "owner" and m.id != member.id]
            if not outros_donos:
                flash("Não pode retirar o cargo de Dono sem definir outro Dono primeiro.", "danger")
                return render_template("team/edit.html", member=member)

        if not name or not email:
            flash("Nome e e-mail são obrigatórios.", "danger")
            return render_template("team/edit.html", member=member)

        existente = User.buscar_por_email(email)
        if existente and existente.id != member.id:
            flash("Este e-mail já se encontra em utilização por outro utilizador.", "danger")
            return render_template("team/edit.html", member=member)

        member.name = name
        member.email = email
        member.role = role

        if new_password:
            if len(new_password) < 6:
                flash("A nova palavra-passe deve ter pelo menos 6 carateres.", "warning")
                return render_template("team/edit.html", member=member)
            member.set_password(new_password)

        member.salvar()
        flash("Dados do colaborador atualizados com sucesso!", "success")
        return redirect(url_for("team.list_members"))

    return render_template("team/edit.html", member=member)

@team_bp.route("/<int:member_id>/excluir", methods=["POST"])
@login_required
@role_required(["owner", "manager"])
def delete_member(member_id):
    store_id = session.get("store_id")
    current_user_id = session.get("user_id")
    current_role = session.get("user_role")

    member = User.buscar_por_id(member_id)

    if not member or member.store_id != store_id:
        flash("Colaborador não encontrado.", "danger")
        return redirect(url_for("team.list_members"))

    if member.id == current_user_id:
        flash("Não é permitido remover a sua própria conta ativa.", "danger")
        return redirect(url_for("team.list_members"))

    if current_role == "manager" and member.role != "operator":
        flash("Gerentes apenas podem remover operadores.", "danger")
        return redirect(url_for("team.list_members"))

    if member.role == "owner":
        todos = User.listar_por_loja(store_id)
        outros_donos = [m for m in todos if m.role == "owner" and m.id != member.id]
        if not outros_donos:
            flash("Não é possível remover o único Dono ativo da loja.", "danger")
            return redirect(url_for("team.list_members"))

    User.excluir(member_id, store_id)
    flash(f"Colaborador '{member.name}' removido com sucesso.", "info")
    return redirect(url_for("team.list_members"))