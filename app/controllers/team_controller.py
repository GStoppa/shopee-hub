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

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")
        role = request.form.get("role", "operator")

        if not name or not email or not password:
            flash("Todos os campos são obrigatórios.", "danger")
            return render_template("team/form.html", member=None)

        if User.buscar_por_email(email):
            flash("Este e-mail já está em uso por outro usuário.", "danger")
            return render_template("team/form.html", member=None)

        if role not in ["owner", "manager", "operator"]:
            role = "operator"

        novo_membro = User(name=name, email=email, store_id=store_id, role=role)
        novo_membro.set_password(password)
        novo_membro.salvar()

        flash(f"Membro '{name}' cadastrado com sucesso!", "success")
        return redirect(url_for("team.list_members"))

    return render_template("team/form.html", member=None)

@team_bp.route("/<int:member_id>/editar", methods=["GET", "POST"])
@team_bp.route("/<int:user_id>/editar", methods=["GET", "POST"])
@login_required
@role_required(["owner", "manager"])
def edit_member(member_id=None, user_id=None):
    uid = member_id or user_id
    store_id = session.get("store_id")
    member = User.buscar_por_id(uid)

    if not member or member.store_id != store_id:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("team.list_members"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role", member.role)

        if not name or not email:
            flash("Nome e e-mail são obrigatórios.", "danger")
            return render_template("team/edit.html", member=member)

        existente = User.buscar_por_email(email)
        if existente and existente.id != member.id:
            flash("Este e-mail já está em uso por outro usuário.", "danger")
            return render_template("team/edit.html", member=member)

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
@team_bp.route("/<int:user_id>/excluir", methods=["POST"])
@login_required
@role_required(["owner"])
def delete_member(member_id=None, user_id=None):
    uid = member_id or user_id
    store_id = session.get("store_id")
    member = User.buscar_por_id(uid)

    if not member or member.store_id != store_id:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("team.list_members"))

    if member.id == session.get("user_id"):
        flash("Você não pode excluir sua própria conta de acesso.", "warning")
        return redirect(url_for("team.list_members"))

    User.excluir(uid, store_id)
    flash(f"Membro '{member.name}' excluído com sucesso.", "info")
    return redirect(url_for("team.list_members"))