import unittest
from unittest.mock import patch

from flask import Flask

from app.routes.payments import payment_blueprint


def build_test_app():
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY="stage-15e-test-secret",
    )

    @app.get("/")
    def index():
        return "index"

    @app.get("/login")
    def auth_login():
        return "login"

    @app.get("/appointments")
    def appointments_list():
        return "appointments"

    app.add_url_rule(
        "/login-alias",
        endpoint="auth.login",
        view_func=auth_login,
    )
    app.add_url_rule(
        "/appointments-alias",
        endpoint="appointments.my_appointments",
        view_func=appointments_list,
    )

    app.register_blueprint(payment_blueprint)

    return app


class PaymentWorkflowTests(unittest.TestCase):

    def setUp(self):
        self.app = build_test_app()
        self.client = self.app.test_client()

    def login_as_user(self, user_id=3):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id
            session["role"] = "user"
            session["full_name"] = "Test User"

    def test_unauthenticated_user_is_redirected_to_login(self):
        response = self.client.get(
            "/appointments/5/payment",
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login-alias", response.location)

    @patch(
        "app.routes.payments.get_appointment_for_payment"
    )
    def test_cross_user_appointment_is_not_exposed(
        self,
        get_appointment,
    ):
        self.login_as_user(user_id=3)
        get_appointment.return_value = None

        response = self.client.get(
            "/appointments/999/payment",
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            "/appointments-alias",
            response.location,
        )

    @patch(
        "app.routes.payments.get_appointment_for_payment"
    )
    def test_cancelled_appointment_cannot_accept_payment(
        self,
        get_appointment,
    ):
        self.login_as_user()
        get_appointment.return_value = {
            "id": 3,
            "status": "cancelled",
        }

        response = self.client.get(
            "/appointments/3/payment",
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            "/appointments-alias",
            response.location,
        )

    @patch(
        "app.routes.payments.find_payment_proof_by_appointment"
    )
    @patch(
        "app.routes.payments.get_appointment_for_payment"
    )
    def test_duplicate_payment_proof_is_blocked(
        self,
        get_appointment,
        find_payment,
    ):
        self.login_as_user()
        get_appointment.return_value = {
            "id": 5,
            "status": "pending",
        }
        find_payment.return_value = {
            "id": 3,
            "appointment_id": 5,
        }

        response = self.client.get(
            "/appointments/5/payment",
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            "/appointments-alias",
            response.location,
        )


if __name__ == "__main__":
    unittest.main()
