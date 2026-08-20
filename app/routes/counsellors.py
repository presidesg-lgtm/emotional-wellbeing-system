from datetime import date

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
    create_appointment,
)

from app.repositories.counsellor_repository import (
    get_available_counsellors,
    get_counsellor_profile_by_id,
)


counsellor_blueprint = Blueprint(
    "counsellors",
    __name__,
)


def user_access_required():
    """
    Ensure the current session belongs to
    an authenticated normal user.
    """

    if "user_id" not in session:
        return redirect(
            url_for("auth.login")
        )

    if session.get("role") != "user":
        return redirect(
            url_for("index")
        )

    return None


@counsellor_blueprint.get("/counsellors")
def counsellor_list():
    """
    Display available counsellors to authenticated users.
    """

    access_response = user_access_required()

    if access_response is not None:
        return access_response

    counsellors = get_available_counsellors()

    return render_template(
        "counsellors.html",
        counsellors=counsellors,
    )


@counsellor_blueprint.route(
    "/counsellors/<int:profile_id>/book",
    methods=["GET", "POST"],
)
def book_appointment(profile_id: int):
    """
    Display the booking form and create a pending
    appointment request for the selected counsellor.
    """

    access_response = user_access_required()

    if access_response is not None:
        return access_response

    counsellor = get_counsellor_profile_by_id(
        profile_id
    )

    if counsellor is None:
        flash(
            "The selected counsellor could not be found.",
            "error",
        )

        return redirect(
            url_for(
                "counsellors.counsellor_list"
            )
        )

    if request.method == "POST":
        appointment_date = request.form.get(
            "appointment_date",
            "",
        ).strip()

        start_time = request.form.get(
            "start_time",
            "",
        ).strip()

        if not appointment_date:
            flash(
                "Please select an appointment date.",
                "error",
            )

            return render_template(
                "book_appointment.html",
                counsellor=counsellor,
                minimum_date=date.today().isoformat(),
            )

        if not start_time:
            flash(
                "Please select an appointment time.",
                "error",
            )

            return render_template(
                "book_appointment.html",
                counsellor=counsellor,
                minimum_date=date.today().isoformat(),
            )

        if appointment_date < date.today().isoformat():
            flash(
                "Appointment date cannot be in the past.",
                "error",
            )

            return render_template(
                "book_appointment.html",
                counsellor=counsellor,
                minimum_date=date.today().isoformat(),
            )

        appointment_id = create_appointment(
            user_id=session["user_id"],
            counsellor_profile_id=profile_id,
            appointment_date=appointment_date,
            start_time=start_time,
        )

        flash(
            "Appointment request submitted successfully. "
            f"Reference #{appointment_id}.",
            "success",
        )

        return redirect(
            url_for(
                "counsellors.counsellor_list"
            )
        )

    return render_template(
        "book_appointment.html",
        counsellor=counsellor,
        minimum_date=date.today().isoformat(),
    )