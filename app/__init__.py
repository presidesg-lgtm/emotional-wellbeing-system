from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from werkzeug.exceptions import RequestEntityTooLarge

from config import Config

from app.security import (
    enforce_active_authenticated_session,
    get_csrf_token,
    validate_csrf_request,
)

from app.routes.admin import admin_blueprint
from app.routes.analysis import analysis_blueprint
from app.routes.appointments import appointment_blueprint
from app.routes.auth import auth_blueprint
from app.routes.counsellor_portal import (
    counsellor_portal_blueprint,
)
from app.routes.counsellors import counsellor_blueprint
from app.routes.dashboard import dashboard_blueprint
from app.routes.forum import forum_blueprint
from app.routes.history import history_blueprint
from app.routes.payments import payment_blueprint


def create_app() -> Flask:
    """
    Create and configure the Flask application.
    """

    app = Flask(__name__)

    app.config.from_object(Config)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY must be configured in the environment."
        )

    app.jinja_env.globals["csrf_token"] = get_csrf_token

    app.before_request(validate_csrf_request)
    app.before_request(enforce_active_authenticated_session)

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

    app.register_blueprint(
        payment_blueprint
    )

    app.register_blueprint(
        forum_blueprint
    )


    @app.errorhandler(RequestEntityTooLarge)
    def handle_request_too_large(error):
        """
        Return users to the payment form when an upload exceeds the
        configured request-size limit.
        """

        if (
            request.endpoint == "payments.submit_payment_proof"
            and request.view_args
            and "appointment_id" in request.view_args
        ):
            flash(
                "Payment proof files must not exceed 5 MB.",
                "error",
            )
            return redirect(
                url_for(
                    "payments.submit_payment_proof",
                    appointment_id=request.view_args["appointment_id"],
                )
            )

        return (
            "The submitted request is too large.",
            413,
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

        if session.get("role") != "user":
            session.clear()
            return redirect(
                url_for("auth.login")
            )

        return render_template(
            "index.html"
        )

    return app
