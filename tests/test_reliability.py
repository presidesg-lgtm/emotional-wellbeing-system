import io
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from flask import Flask

from app.routes.analysis import analysis_blueprint
from app.routes.payments import payment_blueprint


class ReliabilityTests(unittest.TestCase):

    def test_analysis_returns_503_when_model_service_fails(self):
        app = Flask(__name__)
        app.config.update(
            TESTING=True,
            SECRET_KEY="stage-15f-test-secret",
        )
        app.register_blueprint(analysis_blueprint)

        client = app.test_client()

        with client.session_transaction() as session:
            session["user_id"] = 3
            session["role"] = "user"

        with patch(
            "app.routes.analysis.get_emotion_service"
        ) as get_service:
            get_service.side_effect = RuntimeError(
                "simulated model loading failure"
            )

            response = client.post(
                "/api/analyse",
                json={"text": "I feel calm today."},
            )

        self.assertEqual(response.status_code, 503)

        payload = response.get_json()

        self.assertFalse(payload["success"])
        self.assertIn(
            "temporarily unavailable",
            payload["error"].lower(),
        )
        self.assertNotIn(
            "simulated model loading failure",
            payload["error"],
        )

    @patch(
        "app.routes.payments.find_payment_proof_by_appointment"
    )
    @patch(
        "app.routes.payments.get_appointment_for_payment"
    )
    @patch(
        "app.routes.payments.validate_payment_proof"
    )
    @patch(
        "app.routes.payments.create_payment_proof"
    )
    def test_payment_database_failure_removes_saved_file(
        self,
        create_payment,
        validate_upload,
        get_appointment,
        find_payment,
    ):
        app = Flask(
            __name__,
            template_folder="../app/templates",
        )
        app.config.update(
            TESTING=True,
            SECRET_KEY="stage-15f-test-secret",
        )

        app.jinja_env.globals["csrf_token"] = (
            lambda: "stage-15f-test-token"
        )

        @app.get("/")
        def index():
            return "index"

        @app.get("/appointments")
        def appointment_list():
            return "appointments"

        @app.get("/login")
        def login():
            return "login"

        app.add_url_rule(
            "/appointments-alias",
            endpoint="appointments.my_appointments",
            view_func=appointment_list,
        )
        app.add_url_rule(
            "/login-alias",
            endpoint="auth.login",
            view_func=login,
        )

        # The Stage 15H sidebar references the normal-user navigation
        # endpoints. The miniature Flask app used by this isolated
        # reliability test needs harmless stand-in routes so Jinja can
        # build those links while rendering the real payment template.
        app.add_url_rule(
            "/dashboard-alias",
            endpoint="dashboard.dashboard",
            view_func=lambda: "dashboard",
        )
        app.add_url_rule(
            "/history-alias",
            endpoint="history.mood_history",
            view_func=lambda: "history",
        )
        app.add_url_rule(
            "/counsellors-alias",
            endpoint="counsellors.counsellor_list",
            view_func=lambda: "counsellors",
        )
        app.add_url_rule(
            "/forum-alias",
            endpoint="forum.forum_home",
            view_func=lambda: "forum",
        )
        app.add_url_rule(
            "/profile-alias",
            endpoint="auth.profile",
            view_func=lambda: "profile",
        )
        app.add_url_rule(
            "/logout-alias",
            endpoint="auth.logout",
            view_func=lambda: "logout",
            methods=["POST"],
        )

        app.register_blueprint(payment_blueprint)

        get_appointment.return_value = {
            "id": 8,
            "status": "pending",
        }
        find_payment.return_value = None
        validate_upload.return_value = SimpleNamespace(
            is_valid=True,
            message="valid",
            detected_extension="pdf",
        )
        create_payment.side_effect = RuntimeError(
            "simulated database failure"
        )

        client = app.test_client()

        with client.session_transaction() as session:
            session["user_id"] = 3
            session["role"] = "user"

        with tempfile.TemporaryDirectory() as temporary_directory:
            old_cwd = Path.cwd()

            try:
                os.chdir(temporary_directory)

                response = client.post(
                    "/appointments/8/payment",
                    data={
                        "payment_proof": (
                            io.BytesIO(b"%PDF-1.7\nexample"),
                            "proof.pdf",
                        )
                    },
                    content_type="multipart/form-data",
                )

                upload_directory = (
                    Path(temporary_directory)
                    / "uploads"
                    / "payment_proofs"
                )

                saved_files = (
                    list(upload_directory.iterdir())
                    if upload_directory.exists()
                    else []
                )

            finally:
                os.chdir(old_cwd)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(saved_files, [])

    def test_unknown_route_returns_controlled_404(self):
        from app import create_app

        with patch(
            "app.security.find_user_by_id"
        ):
            app = create_app()
            app.config.update(
                TESTING=True,
                SECRET_KEY="stage-15f-test-secret",
            )

            client = app.test_client()
            response = client.get(
                "/this-page-does-not-exist"
            )

        self.assertEqual(response.status_code, 404)
        self.assertIn(
            b"Page not found",
            response.data,
        )


if __name__ == "__main__":
    unittest.main()
