from datetime import datetime
from flask import Flask, render_template, flash, redirect, request
from config import Config

def format_currency(value):
    try:
        val = float(value)
        formatted = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatted}"
    except (ValueError, TypeError):
        return "R$ 0,00"

def format_datetime(value):
    try:
        if not value:
            return "—"
        s = str(value)
        if len(s) >= 19 and s[4] == "-" and s[7] == "-":
            data, hora = s[:10], s[11:19]
            ano, mes, dia = data.split("-")
            return f"{dia}/{mes}/{ano} {hora}"
        return s
    except Exception:
        return value

def format_date(value):
    try:
        if not value:
            return "—"
        s = str(value)[:10]
        if len(s) == 10 and s[4] == "-" and s[7] == "-":
            ano, mes, dia = s.split("-")
            return f"{dia}/{mes}/{ano}"
        return s
    except Exception:
        return value

def create_app():
    app = Flask(__name__, template_folder="views", static_folder="static")
    app.config.from_object(Config)

    with app.app_context():
        try:
            from init_db import inicializar_banco
            inicializar_banco()
        except Exception as e:
            print(f"Aviso durante a inicialização automática do banco: {e}")

    app.jinja_env.filters["currency"] = format_currency
    app.jinja_env.filters["datetime_format"] = format_datetime
    app.jinja_env.filters["date_format"] = format_date

    from app.controllers.auth_controller import auth_bp
    from app.controllers.main_controller import main_bp
    from app.controllers.product_controller import product_bp
    from app.controllers.stock_controller import stock_bp
    from app.controllers.profile_controller import profile_bp
    from app.controllers.team_controller import team_bp
    from app.controllers.store_controller import store_bp
    from app.controllers.category_controller import category_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(store_bp)
    app.register_blueprint(category_bp)

    @app.route("/favicon.ico")
    def favicon():
        return "", 204

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(413)
    def file_too_large(error):
        flash("O ficheiro enviado excede o limite máximo permitido de 2MB.", "danger")
        destino = request.referrer or "/"
        return redirect(destino)

    return app