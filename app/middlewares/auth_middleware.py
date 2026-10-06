from functools import wraps
from flask import session, redirect, url_for, flash, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Por favor, inicie sessão para aceder a esta página.", "warning")
            return redirect(url_for("auth.login", next=request.endpoint))
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("auth.login"))
            
            user_role = session.get("user_role")
            if user_role not in allowed_roles:
                flash("Não tem permissão para realizar esta operação.", "danger")
                return redirect(url_for("main.welcome"))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator