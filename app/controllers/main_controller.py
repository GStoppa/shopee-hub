from flask import Blueprint, render_template, session, redirect, url_for
from app.middlewares.auth_middleware import login_required

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("main.welcome"))
    return redirect(url_for("auth.login"))

@main_bp.route("/welcome")
@login_required
def welcome():
    user_data = {
        "name": session.get("user_name"),
        "email": session.get("user_email")
    }
    return render_template("main/welcome.html", user=user_data)