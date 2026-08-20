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
from app.routes.appointments import appointment_blueprint
from app.routes.auth import auth_blueprint
from app.routes.counsellor_portal import (
    counsellor_portal_blueprint,
)
from app.routes.counsellors import counsellor_blueprint
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

    app.register_blueprint(
        counsellor_blueprint
    )

    app.register_blueprint(
        counsellor_portal_blueprint
    )

    app.register_blueprint(
        appointment_blueprint
    )

    @app.get("/")
    def index():
        """
        Display the correct landing page
        according to the authenticated role.
        """

        if "user_id" not in session:
            return redirect(
                url_for("auth.login")
            )

        if session.get("role") == "admin":
            return redirect(
                url_for("admin.dashboard")
            )

        if session.get("role") == "counsellor":
            return redirect(
                url_for("counsellor_portal.dashboard")
            )

        return render_template(
            "index.html"
        )

    return app