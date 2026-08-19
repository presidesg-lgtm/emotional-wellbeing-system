from flask import (
    Flask,
    redirect,
    render_template,
    session,
    url_for,
)

from config import Config

from app.routes.admin import admin_blueprint
from app.routes.analysis import analysis_blueprint
from app.routes.auth import auth_blueprint
from app.routes.dashboard import dashboard_blueprint
from app.routes.history import history_blueprint


def create_app() -> Flask:
    """
    Create and configure the Flask application.
    """

    app = Flask(__name__)

    app.config.from_object(Config)

    app.register_blueprint(
        analysis_blueprint
    )

    app.register_blueprint(
        auth_blueprint
    )

    app.register_blueprint(
        history_blueprint
    )

    app.register_blueprint(
        dashboard_blueprint
    )

    app.register_blueprint(
        admin_blueprint
    )

    @app.get("/")
    def index():
        if "user_id" not in session:
            return redirect(
                url_for("auth.login")
            )

        if session.get("role") == "admin":
            return redirect(
                url_for("admin.dashboard")
            )

        return render_template(
            "index.html"
        )

    return app