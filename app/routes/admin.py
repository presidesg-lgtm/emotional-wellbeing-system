from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.repositories.user_repository import (
    get_all_users,
    get_user_statistics,
    update_user_active_status,
)


admin_blueprint = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
)


def admin_access_required():
    """
    Check whether the current session belongs to
    an authenticated administrator.

    Returns a redirect response when access should
    be denied, otherwise returns None.
    """

    if "user_id" not in session:
        flash(
            "Please log in to continue.",
            "error",
        )

        return redirect(
            url_for("auth.login")
        )

    if session.get("role") != "admin":
        flash(
            "You do not have permission to access "
            "the administrator area.",
            "error",
        )

        return redirect(
            url_for("index")
        )

    return None


@admin_blueprint.get("/")
def dashboard():
    """
    Display the administrator dashboard.
    """

    access_response = admin_access_required()

    if access_response is not None:
        return access_response

    statistics = get_user_statistics()

    users = get_all_users()

    return render_template(
        "admin_dashboard.html",
        statistics=statistics,
        users=users,
    )


@admin_blueprint.post(
    "/users/<int:user_id>/status"
)
def update_account_status(user_id: int):
    """
    Activate or deactivate a registered account.

    Only administrators may perform this action.
    Administrators cannot deactivate their own
    currently authenticated account.
    """

    access_response = admin_access_required()

    if access_response is not None:
        return access_response

    action = request.form.get(
        "action",
        "",
    )

    if action not in {
        "activate",
        "deactivate",
    }:
        flash(
            "Invalid account-status action.",
            "error",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    if (
        action == "deactivate"
        and user_id == session["user_id"]
    ):
        flash(
            "You cannot deactivate your own "
            "administrator account while logged in.",
            "error",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    is_active = action == "activate"

    updated = update_user_active_status(
        user_id=user_id,
        is_active=is_active,
    )

    if not updated:
        flash(
            "The requested account could not be found.",
            "error",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    if is_active:
        flash(
            "Account activated successfully.",
            "success",
        )
    else:
        flash(
            "Account deactivated successfully.",
            "success",
        )

    return redirect(
        url_for("admin.dashboard")
    )