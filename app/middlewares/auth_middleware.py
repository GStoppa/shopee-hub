from functools import wraps
from flask import session, redirect, url_for, abort
from app.models.user_model import User
from app.models.store_model import Store

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("auth.login"))

        user = User.buscar_por_id(user_id)
        if not user:
            session.clear()
            return redirect(url_for("auth.login"))

        session["user_name"] = user.name
        session["user_role"] = user.role
        session["store_id"] = user.store_id

        if user.store_id:
            store = Store.buscar_por_id(user.store_id)
            session["store_name"] = store.name if store else "Minha Loja"
            session["store_logo_url"] = store.logo_url if store and store.logo_url else None

        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    if len(allowed_roles) == 1 and isinstance(allowed_roles[0], (list, tuple, set)):
        roles_set = set(allowed_roles[0])
    else:
        roles_set = set(allowed_roles)

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get("user_id")
            if not user_id:
                return redirect(url_for("auth.login"))

            user = User.buscar_por_id(user_id)
            if not user:
                session.clear()
                return redirect(url_for("auth.login"))

            session["user_name"] = user.name
            session["user_role"] = user.role
            session["store_id"] = user.store_id

            if user.role not in roles_set:
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator