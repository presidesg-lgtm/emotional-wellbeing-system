from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.repositories.appointment_repository import (
    get_appointments_for_counsellor,
    update_appointment_status,
)


counsellor_portal_blueprint = Blueprint(
    "counsellor_portal",
    __name__,
    url_prefix="/counsellor",
)


def counsellor_access_required():
    """
    Ensure the current session belongs to
    an authenticated counsellor.
    """

    if "user_id" not in session:
        return redirect(
            url_for("auth.login")
        )

    if session.get("role") != "counsellor":
        flash(
            "You do not have permission to access "
            "the counsellor area.",
            "error",
        )

        return redirect(
            url_for("index")
        )

    return None


@counsellor_portal_blueprint.get("/")
def dashboard():
    """
    Display appointments assigned to
    the logged-in counsellor.
    """

    access_response = counsellor_access_required()

    if access_response is not None:
        return access_response

    appointments = get_appointments_for_counsellor(
        session["user_id"]
    )

    return render_template(
        "counsellor_dashboard.html",
        appointments=appointments,
    )


@counsellor_portal_blueprint.post(
    "/appointments/<int:appointment_id>/status"
)
def update_status(appointment_id: int):
    """
    Confirm, reject, or complete an appointment.
    """

    access_response = counsellor_access_required()

    if access_response is not None:
        return access_response

    action = request.form.get(
        "action",
        "",
    )

    allowed_actions = {
        "confirm": "confirmed",
        "reject": "rejected",
        "complete": "completed",
        "cancel": "cancelled",
    }

    if action not in allowed_actions:
        flash(
            "Invalid appointment action.",
            "error",
        )

        return redirect(
            url_for("counsellor_portal.dashboard")
        )

    updated = update_appointment_status(
        appointment_id=appointment_id,
        counsellor_user_id=session["user_id"],
        status=allowed_actions[action],
    )

    if not updated:
        flash(
            "Appointment could not be updated.",
            "error",
        )
    else:
        flash(
            "Appointment status updated successfully.",
            "success",
        )

    return redirect(
        url_for("counsellor_portal.dashboard")
    )