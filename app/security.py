from __future__ import annotations

import secrets
from hmac import compare_digest

from flask import (
    flash,
    jsonify,
    redirect,
    request,
    session,
    url_for,
)

from app.repositories.user_repository import find_user_by_id


CSRF_SESSION_KEY = "csrf_token"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}


def get_csrf_token() -> str:
    """Return the current session CSRF token, creating one if needed."""

    token = session.get(CSRF_SESSION_KEY)

    if not token:
        token = secrets.token_urlsafe(32)
        session[CSRF_SESSION_KEY] = token

    return token


def validate_csrf_request():
    """Reject state-changing requests that do not contain a valid CSRF token."""

    if request.method in SAFE_METHODS:
        return None

    expected_token = session.get(CSRF_SESSION_KEY)
    submitted_token = (
        request.headers.get("X-CSRF-Token")
        or request.form.get("csrf_token")
    )

    if (
        not expected_token
        or not submitted_token
        or not compare_digest(
            str(expected_token),
            str(submitted_token),
        )
    ):
        if request.path.startswith("/api/"):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": (
                            "Security validation failed. "
                            "Refresh the page and try again."
                        ),
                    }
                ),
                400,
            )

        flash(
            "Security validation failed. Refresh the page and try again.",
            "error",
        )

        if "user_id" in session:
            return redirect(url_for("index"))

        return redirect(url_for("auth.login"))

    return None


def enforce_active_authenticated_session():
    """Invalidate an authenticated session when its account is gone or inactive.

    The database role and display name are also refreshed so permission changes
    take effect without requiring the user to sign out manually.
    """

    if "user_id" not in session:
        return None

    if request.endpoint == "static":
        return None

    user = find_user_by_id(session["user_id"])

    if user is None or not user["is_active"]:
        session.clear()

        if request.path.startswith("/api/"):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": (
                            "Your session is no longer active. "
                            "Please log in again."
                        ),
                    }
                ),
                401,
            )

        flash(
            "Your account is no longer active. Please log in again.",
            "error",
        )
        return redirect(url_for("auth.login"))

    session["role"] = user["role"]
    session["full_name"] = user["full_name"]

    return None
