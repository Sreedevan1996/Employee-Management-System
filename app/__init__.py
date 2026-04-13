from flask import Flask, render_template

from app.config import config_by_name
from app.extensions import init_extensions
from app.routes import register_blueprints
from app.utils.logging_config import configure_logging
from app.utils.security import configure_security, register_security_headers


def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    config_class = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_class)
    config_class.init_app(app)

    # Security config first
    configure_security(app)

    # Extensions
    init_extensions(app)

    # Logging
    configure_logging(app)

    # Response security headers
    register_security_headers(app)

    # Blueprints
    register_blueprints(app)

    # Error handlers
    register_error_handlers(app)

    return app


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template("errors/500.html"), 500