from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__, template_folder="views", static_folder="static")
    app.config.from_object(Config)

    from app.controllers.auth_controller import auth_bp
    from app.controllers.main_controller import main_bp
    from app.controllers.product_controller import product_bp
    from app.controllers.profile_controller import profile_bp
    from app.controllers.team_controller import team_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(team_bp)

    return app