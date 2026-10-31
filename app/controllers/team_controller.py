from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.middlewares.auth_middleware import login_required, role_required
from app.models.user_model import User

team_bp = Blueprint("team", __name__, url_prefix="/team")

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
    user_role = session.get("user_role")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")
        role = request.form.get("role", "operator")

        if not name or not email or not password:
            flash("Todos os campos são obrigatórios.", "danger")
            return render_template("team/form.html", member=None, form_data=request.form)

        if "@" not in email or "." not in email.split("@")[-1]:
            flash("Insira um endereço de e-mail válido.", "danger")
            return render_template("team/form.html", member=None, form_data=request.form)

        if len(password) < 6:
            flash("A senha deve conter no mínimo 6 caracteres.", "danger")
            return render_template("team/form.html", member=None, form_data=request.form)

        if user_role == "manager" and role == "owner":
            flash("Gerentes não possuem permissão para criar usuários com função de Proprietário.", "danger")
            return render_template("team/form.html", member=None, form_data=request.form)

        if User.buscar_por_email(email):
            flash("Este e-mail já está em uso por outro usuário.", "danger")
            return render_template("team/form.html", member=None, form_data=request.form)

        if role not in ["owner", "manager", "operator"]:
            role = "operator"

        novo_membro = User(name=name, email=email, store_id=store_id, role=role)
        novo_membro.set_password(password)
        novo_membro.salvar()

        flash(f"Membro '{name}' cadastrado com sucesso!", "success")
        return redirect(url_for("team.list_members"))

    return render_template("team/form.html", member=None)

@team_bp.route("/<int:member_id>/editar", methods=["GET", "POST"])
@login_required
@role_required(["owner", "manager"])
def edit_member(member_id):
    store_id = session.get("store_id")
    current_user_role = session.get("user_role")
    current_user_id = session.get("user_id")

    member = User.buscar_por_id(member_id)
    if not member or member.store_id != store_id:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("team.list_members"))

    if current_user_role == "manager" and member.role == "owner":
        flash("Gerentes não possuem permissão para alterar dados de um Proprietário.", "danger")
        return redirect(url_for("team.list_members"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role", member.role)
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not name or not email:
            flash("Nome e e-mail são obrigatórios.", "danger")
            return render_template("team/edit.html", member=member)

        if "@" not in email or "." not in email.split("@")[-1]:
            flash("Insira um endereço de e-mail válido.", "danger")
            return render_template("team/edit.html", member=member)

        if current_user_role == "manager" and role == "owner":
            flash("Apenas proprietários podem conceder permissão de Proprietário.", "danger")
            return render_template("team/edit.html", member=member)

        if member.id == current_user_id and member.role == "owner" and role != "owner":
            flash("Você não pode revogar sua própria permissão de Proprietário.", "danger")
            return render_template("team/edit.html", member=member)

        existente = User.buscar_por_email(email)
        if existente and existente.id != member.id:
            flash("Este e-mail já está em uso por outro usuário.", "danger")
            return render_template("team/edit.html", member=member)

        # Redefinição opcional de senha
        if password:
            if len(password) < 6:
                flash("A nova senha deve ter no mínimo 6 caracteres.", "danger")
                return render_template("team/edit.html", member=member)
            if password != confirm_password:
                flash("A confirmação de senha não confere com a nova senha digitada.", "danger")
                return render_template("team/edit.html", member=member)
            member.set_password(password)

        if role not in ["owner", "manager", "operator"]:
            role = member.role

        member.name = name
        member.email = email
        member.role = role
        member.salvar()

        flash(f"Membro '{name}' atualizado com sucesso!", "success")
        return redirect(url_for("team.list_members"))

    return render_template("team/edit.html", member=member)

@team_bp.route("/<int:member_id>/excluir", methods=["POST"])
@login_required
@role_required(["owner", "manager"])
def delete_member(member_id):
    store_id = session.get("store_id")
    current_user_role = session.get("user_role")

    member = User.buscar_por_id(member_id)
    if not member or member.store_id != store_id:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("team.list_members"))

    if member.id == session.get("user_id"):
        flash("Você não pode excluir sua própria conta de acesso.", "warning")
        return redirect(url_for("team.list_members"))

    if current_user_role == "manager" and member.role == "owner":
        flash("Gerentes não possuem permissão para excluir um Proprietário.", "danger")
        return redirect(url_for("team.list_members"))

    User.excluir(member_id, store_id)
    flash(f"Membro '{member.name}' excluído com sucesso.", "info")
    return redirect(url_for("team.list_members"))