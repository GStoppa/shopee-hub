from functools import wraps
from flask import session, redirect, url_for, flash, request, abort

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Por favor, inicie sessão para aceder a esta página.", "warning")
            return redirect(url_for("auth.login", next=request.endpoint))
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    """Interrompe a requisição com código HTTP 403 caso o cargo não tenha autorização."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("auth.login"))
            
            user_role = session.get("user_role")
            if user_role not in allowed_roles:
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator