from app.routes.auth import auth_bp
from app.routes.main import main_bp
from app.routes.admin import admin_bp
from app.routes.employee import employee_bp
from app.routes.profile import profile_bp


def register_blueprints(app):
    """
    Register all application blueprints.
    """
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(profile_bp)