from datetime import (
    date,
    datetime,
)

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

from app.repositories.counsellor_repository import (
    create_availability_slot,
    delete_unbooked_availability_slot,
    get_availability_slots_for_counsellor,
    get_counsellor_profile_by_user_id,
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
    Display availability slots and appointments
    belonging to the logged-in counsellor.
    """

    access_response = counsellor_access_required()

    if access_response is not None:
        return access_response

    counsellor_profile = (
        get_counsellor_profile_by_user_id(
            session["user_id"]
        )
    )

    if counsellor_profile is None:
        flash(
            "Counsellor profile could not be found.",
            "error",
        )

        return redirect(
            url_for("auth.logout")
        )

    availability_slots = (
        get_availability_slots_for_counsellor(
            counsellor_profile["profile_id"]
        )
    )

    appointments = get_appointments_for_counsellor(
        session["user_id"]
    )

    return render_template(
        "counsellor_dashboard.html",
        counsellor_profile=counsellor_profile,
        availability_slots=availability_slots,
        appointments=appointments,
        minimum_date=date.today().isoformat(),
    )


@counsellor_portal_blueprint.post("/availability")
def add_availability():
    """
    Allow a counsellor to publish an available
    appointment date and start time.
    """

    access_response = counsellor_access_required()

    if access_response is not None:
        return access_response

    counsellor_profile = (
        get_counsellor_profile_by_user_id(
            session["user_id"]
        )
    )

    if counsellor_profile is None:
        flash(
            "Counsellor profile could not be found.",
            "error",
        )

        return redirect(
            url_for("counsellor_portal.dashboard")
        )

    slot_date = request.form.get(
        "slot_date",
        "",
    ).strip()

    start_time = request.form.get(
        "start_time",
        "",
    ).strip()

    if not slot_date or not start_time:
        flash(
            "Please select both a date and time.",
            "error",
        )

        return redirect(
            url_for("counsellor_portal.dashboard")
        )

    try:
        slot_datetime = datetime.strptime(
            f"{slot_date} {start_time}",
            "%Y-%m-%d %H:%M",
        )

    except ValueError:
        flash(
            "Please enter a valid appointment date and time.",
            "error",
        )

        return redirect(
            url_for("counsellor_portal.dashboard")
        )

    if slot_datetime <= datetime.now():
        flash(
            "Availability must be scheduled for a future date and time.",
            "error",
        )

        return redirect(
            url_for("counsellor_portal.dashboard")
        )

    created = create_availability_slot(
        counsellor_profile_id=(
            counsellor_profile["profile_id"]
        ),
        slot_date=slot_date,
        start_time=start_time,
    )

    if not created:
        flash(
            "That availability slot already exists.",
            "error",
        )

    else:
        flash(
            "Availability slot added successfully.",
            "success",
        )

    return redirect(
        url_for("counsellor_portal.dashboard")
    )


@counsellor_portal_blueprint.post(
    "/availability/<int:slot_id>/delete"
)
def delete_availability(slot_id: int):
    """
    Allow the counsellor to remove an unbooked slot.
    """

    access_response = counsellor_access_required()

    if access_response is not None:
        return access_response

    counsellor_profile = (
        get_counsellor_profile_by_user_id(
            session["user_id"]
        )
    )

    if counsellor_profile is None:
        flash(
            "Counsellor profile could not be found.",
            "error",
        )

        return redirect(
            url_for("counsellor_portal.dashboard")
        )

    deleted = delete_unbooked_availability_slot(
        slot_id=slot_id,
        counsellor_profile_id=(
            counsellor_profile["profile_id"]
        ),
    )

    if not deleted:
        flash(
            "Booked availability cannot be removed.",
            "error",
        )

    else:
        flash(
            "Availability slot removed successfully.",
            "success",
        )

    return redirect(
        url_for("counsellor_portal.dashboard")
    )


@counsellor_portal_blueprint.post(
    "/appointments/<int:appointment_id>/status"
)
def update_status(appointment_id: int):
    """
    Confirm, reject, complete, or cancel an appointment.
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