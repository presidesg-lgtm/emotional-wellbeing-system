from pathlib import Path

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from app.repositories.payment_repository import (
    get_all_payment_proofs,
    get_payment_proof_by_id,
    review_payment_proof,
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

    payment_proofs = get_all_payment_proofs()

    return render_template(
        "admin_dashboard.html",
        statistics=statistics,
        users=users,
        payment_proofs=payment_proofs,
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


@admin_blueprint.get(
    "/payments/<int:payment_proof_id>/file"
)
def view_payment_proof(payment_proof_id: int):
    """
    Allow an authenticated administrator to securely
    view a submitted payment-proof file.
    """

    access_response = admin_access_required()

    if access_response is not None:
        return access_response

    payment_proof = get_payment_proof_by_id(
        payment_proof_id
    )

    if payment_proof is None:
        abort(404)

    upload_directory = Path(
        "uploads/payment_proofs"
    ).resolve()

    file_path = (
        upload_directory
        / payment_proof["stored_filename"]
    ).resolve()

    if upload_directory not in file_path.parents:
        abort(404)

    if not file_path.is_file():
        abort(404)

    return send_file(
        file_path,
        download_name=payment_proof[
            "original_filename"
        ],
        as_attachment=False,
    )


@admin_blueprint.post(
    "/payments/<int:payment_proof_id>/review"
)
def review_payment(payment_proof_id: int):
    """
    Verify or reject a submitted payment proof.
    """

    access_response = admin_access_required()

    if access_response is not None:
        return access_response

    action = request.form.get(
        "action",
        "",
    )

    admin_note = request.form.get(
        "admin_note",
        "",
    ).strip()

    allowed_actions = {
        "verify": "verified",
        "reject": "rejected",
    }

    if action not in allowed_actions:
        flash(
            "Invalid payment review action.",
            "error",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    if len(admin_note) > 500:
        flash(
            "Admin note must not exceed 500 characters.",
            "error",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    updated = review_payment_proof(
        payment_proof_id=payment_proof_id,
        status=allowed_actions[action],
        admin_note=admin_note or None,
    )

    if not updated:
        flash(
            "Payment proof could not be updated.",
            "error",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    if action == "verify":
        flash(
            "Payment proof verified successfully.",
            "success",
        )
    else:
        flash(
            "Payment proof rejected.",
            "success",
        )

    return redirect(
        url_for("admin.dashboard")
    )