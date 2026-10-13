from flask import Flask, render_template
from config import Config

def format_currency(value):
    try:
        val = float(value)
        formatted = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatted}"
    except (ValueError, TypeError):
        return "R$ 0,00"

def create_app():
    app = Flask(__name__, template_folder="views", static_folder="static")
    app.config.from_object(Config)

    app.jinja_env.filters["currency"] = format_currency

    from app.controllers.auth_controller import auth_bp
    from app.controllers.main_controller import main_bp
    from app.controllers.product_controller import product_bp
    from app.controllers.profile_controller import profile_bp
    from app.controllers.team_controller import team_bp
    from app.controllers.store_controller import store_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(store_bp)

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    return app