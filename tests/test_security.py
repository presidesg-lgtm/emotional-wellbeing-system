import unittest
from unittest.mock import patch

from flask import Flask, session

from app.security import (
    enforce_active_authenticated_session,
    get_csrf_token,
    validate_csrf_request,
)


def build_test_app():
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY="stage-15e-test-secret",
    )

    @app.get("/")
    def index():
        return "home"

    @app.get("/login")
    def login():
        return "login"

    app.add_url_rule(
        "/login",
        endpoint="auth.login",
        view_func=login,
    )

    return app


class SecurityTests(unittest.TestCase):

    def setUp(self):
        self.app = build_test_app()

    def test_missing_api_csrf_token_is_rejected(self):
        with self.app.test_request_context(
            "/api/analyse",
            method="POST",
        ):
            response = validate_csrf_request()
            self.assertIsNotNone(response)
            body, status = response
            self.assertEqual(status, 400)
            self.assertFalse(body.get_json()["success"])

    def test_valid_csrf_token_is_accepted(self):
        with self.app.test_request_context(
            "/example",
            method="POST",
            data={"csrf_token": "known-token"},
        ):
            session["csrf_token"] = "known-token"
            self.assertIsNone(validate_csrf_request())

    def test_wrong_csrf_token_is_rejected(self):
        with self.app.test_request_context(
            "/api/analyse",
            method="POST",
            headers={"X-CSRF-Token": "wrong-token"},
        ):
            session["csrf_token"] = "expected-token"
            response = validate_csrf_request()
            self.assertEqual(response[1], 400)

    def test_get_request_does_not_require_csrf(self):
        with self.app.test_request_context(
            "/example",
            method="GET",
        ):
            self.assertIsNone(validate_csrf_request())

    def test_csrf_token_is_created_once_per_session(self):
        with self.app.test_request_context("/"):
            first = get_csrf_token()
            second = get_csrf_token()
            self.assertEqual(first, second)
            self.assertGreater(len(first), 20)

    @patch("app.security.find_user_by_id")
    def test_inactive_account_clears_existing_session(
        self,
        find_user,
    ):
        find_user.return_value = {
            "id": 12,
            "full_name": "Inactive User",
            "role": "user",
            "is_active": False,
        }

        with self.app.test_request_context("/"):
            session["user_id"] = 12
            session["role"] = "user"

            response = enforce_active_authenticated_session()

            self.assertIsNotNone(response)
            self.assertNotIn("user_id", session)

    @patch("app.security.find_user_by_id")
    def test_active_account_refreshes_role_and_name(
        self,
        find_user,
    ):
        find_user.return_value = {
            "id": 7,
            "full_name": "Updated Name",
            "role": "counsellor",
            "is_active": True,
        }

        with self.app.test_request_context("/"):
            session["user_id"] = 7
            session["role"] = "user"
            session["full_name"] = "Old Name"

            response = enforce_active_authenticated_session()

            self.assertIsNone(response)
            self.assertEqual(
                session["role"],
                "counsellor",
            )
            self.assertEqual(
                session["full_name"],
                "Updated Name",
            )


if __name__ == "__main__":
    unittest.main()
