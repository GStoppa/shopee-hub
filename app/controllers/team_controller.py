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
    current_user_role = session.get("user_role")

    if request.method == "POST":
        store_id = session.get("store_id")
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "operator")

        if not name or not email or not password:
            flash("Todos os campos são obrigatórios.", "danger")
            return render_template("team/form.html")

        if len(password) < 6:
            flash("A palavra-passe deve conter pelo menos 6 carateres.", "warning")
            return render_template("team/form.html")

        if current_user_role == "manager" and role != "operator":
            flash("Gerentes apenas têm autorização para registar Operadores.", "danger")
            return render_template("team/form.html")

        if role not in ["manager", "operator"]:
            flash("Perfil de acesso inválido.", "danger")
            return render_template("team/form.html")

        if User.buscar_por_email(email):
            flash("Este e-mail já se encontra registado no sistema.", "warning")
            return render_template("team/form.html")

        novo_membro = User(
            name=name,
            email=email,
            store_id=store_id,
            role=role
        )
        novo_membro.set_password(password)
        novo_membro.salvar()

        flash(f"Colaborador '{name}' adicionado à equipa com sucesso!", "success")
        return redirect(url_for("team.list_members"))

    return render_template("team/form.html")

@team_bp.route("/<int:member_id>/editar", methods=["GET", "POST"])
@login_required
@role_required(["owner", "manager"])
def edit_member(member_id):
    store_id = session.get("store_id")
    current_user_id = session.get("user_id")
    current_user_role = session.get("user_role")

    member = User.buscar_por_id(member_id)

    # 1. Validação de isolamento da loja
    if not member or member.store_id != store_id:
        flash("Colaborador não encontrado.", "danger")
        return redirect(url_for("team.list_members"))

    # 2. Regra de hierarquia: gerente não edita dono nem outros gerentes
    if current_user_role == "manager" and member.role in ["owner", "manager"]:
        flash("Não tem permissão para alterar os dados deste colaborador.", "danger")
        return redirect(url_for("team.list_members"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        new_role = request.form.get("role", member.role)
        new_password = request.form.get("password", "").strip()

        if not name or not email:
            flash("Nome e e-mail são obrigatórios.", "danger")
            return render_template("team/edit.html", member=member)

        # 3. Verificação de unicidade do e-mail
        if email != member.email:
            existente = User.buscar_por_email(email)
            if existente and existente.id != member.id:
                flash("Este e-mail já está em uso por outro utilizador.", "warning")
                return render_template("team/edit.html", member=member)

        # 4. Regras de alteração de cargo
        if current_user_role == "manager" and new_role != member.role:
            flash("Gerentes não podem alterar cargos de equipa.", "danger")
            return render_template("team/edit.html", member=member)

        # Se for o dono a rebaixar o próprio cargo, verificar se resta outro dono na loja
        if member.role == "owner" and new_role != "owner":
            todos_membros = User.listar_por_loja(store_id)
            outros_donos = [m for m in todos_membros if m.role == "owner" and m.id != member.id]
            if not outros_donos:
                flash("A loja precisa de pelo menos um Dono ativo.", "danger")
                return render_template("team/edit.html", member=member)

        # 5. Redefinição opcional de palavra-passe
        if new_password:
            if len(new_password) < 6:
                flash("A nova palavra-passe deve ter pelo menos 6 carateres.", "warning")
                return render_template("team/edit.html", member=member)
            member.set_password(new_password)

        member.name = name
        member.email = email
        member.role = new_role
        member.salvar()

        # Atualizar a sessão se o utilizador estiver a editar a si próprio
        if member.id == current_user_id:
            session["user_name"] = member.name
            session["user_email"] = member.email
            session["user_role"] = member.role

        flash(f"Colaborador '{member.name}' atualizado com sucesso!", "success")
        return redirect(url_for("team.list_members"))

    return render_template("team/edit.html", member=member)

@team_bp.route("/<int:member_id>/excluir", methods=["POST"])
@login_required
@role_required(["owner", "manager"])
def delete_member(member_id):
    store_id = session.get("store_id")
    current_user_id = session.get("user_id")
    current_user_role = session.get("user_role")

    member = User.buscar_por_id(member_id)

    # 1. Validação de isolamento da loja
    if not member or member.store_id != store_id:
        flash("Colaborador não encontrado.", "danger")
        return redirect(url_for("team.list_members"))

    # 2. Bloqueio de autoexclusão
    if member.id == current_user_id:
        flash("Não pode remover a sua própria conta através da gestão de equipa.", "danger")
        return redirect(url_for("team.list_members"))

    # 3. Regra de hierarquia: gerente só remove operador
    if current_user_role == "manager" and member.role != "operator":
        flash("Gerentes apenas têm autorização para remover operadores.", "danger")
        return redirect(url_for("team.list_members"))

    # 4. Garantir que a loja mantém pelo menos um Dono
    if member.role == "owner":
        todos_membros = User.listar_por_loja(store_id)
        outros_donos = [m for m in todos_membros if m.role == "owner" and m.id != member.id]
        if not outros_donos:
            flash("Não é possível remover o único Dono ativo da loja.", "danger")
            return redirect(url_for("team.list_members"))

    User.excluir(member_id, store_id)
    flash(f"Colaborador '{member.name}' removido da equipa com sucesso.", "info")
    return redirect(url_for("team.list_members"))