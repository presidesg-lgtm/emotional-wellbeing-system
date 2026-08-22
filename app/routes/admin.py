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

from app.repositories.forum_repository import (
    get_all_forum_posts_for_admin,
    get_all_forum_reports,
    set_forum_post_hidden,
    update_forum_report_status,
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

    forum_reports = get_all_forum_reports()

    forum_posts = get_all_forum_posts_for_admin()

    return render_template(
        "admin_dashboard.html",
        statistics=statistics,
        users=users,
        payment_proofs=payment_proofs,
        forum_reports=forum_reports,
        forum_posts=forum_posts,
    )


@admin_blueprint.post(
    "/users/<int:user_id>/status"
)
def update_account_status(user_id: int):
    """
    Activate or deactivate a registered account.
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


@admin_blueprint.post(
    "/forum/reports/<int:report_id>/moderate"
)
def moderate_forum_report(report_id: int):
    """
    Review a forum report.

    The administrator may hide the reported post
    or dismiss the report without hiding the post.
    """

    access_response = admin_access_required()

    if access_response is not None:
        return access_response

    action = request.form.get(
        "action",
        "",
    )

    post_id = request.form.get(
        "post_id",
        type=int,
    )

    if post_id is None:
        flash(
            "Invalid forum moderation request.",
            "error",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    if action == "hide":
        post_updated = set_forum_post_hidden(
            post_id=post_id,
            is_hidden=True,
        )

        report_updated = update_forum_report_status(
            report_id=report_id,
            status="reviewed",
        )

        if not post_updated or not report_updated:
            flash(
                "Forum moderation action could not be completed.",
                "error",
            )
        else:
            flash(
                "Forum post hidden successfully.",
                "success",
            )

    elif action == "dismiss":
        updated = update_forum_report_status(
            report_id=report_id,
            status="dismissed",
        )

        if not updated:
            flash(
                "Forum report could not be dismissed.",
                "error",
            )
        else:
            flash(
                "Forum report dismissed successfully.",
                "success",
            )

    else:
        flash(
            "Invalid forum moderation action.",
            "error",
        )

    return redirect(
        url_for("admin.dashboard")
    )


@admin_blueprint.post(
    "/forum/posts/<int:post_id>/visibility"
)
def update_forum_post_visibility(post_id: int):
    """
    Allow an administrator to hide or restore
    a forum post.
    """

    access_response = admin_access_required()

    if access_response is not None:
        return access_response

    action = request.form.get(
        "action",
        "",
    )

    if action == "hide":
        is_hidden = True

    elif action == "restore":
        is_hidden = False

    else:
        flash(
            "Invalid forum visibility action.",
            "error",
        )

        return redirect(
            url_for("admin.dashboard")
        )

    updated = set_forum_post_hidden(
        post_id=post_id,
        is_hidden=is_hidden,
    )

    if not updated:
        flash(
            "Forum post could not be updated.",
            "error",
        )

    elif is_hidden:
        flash(
            "Forum post hidden successfully.",
            "success",
        )

    else:
        flash(
            "Forum post restored successfully.",
            "success",
        )

    return redirect(
        url_for("admin.dashboard")
    )