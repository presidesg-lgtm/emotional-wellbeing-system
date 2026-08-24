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
    create_appointment_from_slot,
)

from app.repositories.counsellor_repository import (
    get_available_counsellors,
    get_available_slots_for_profile,
    get_counsellor_profile_by_id,
)

from app.repositories.mood_repository import (
    get_weekly_mood_summary_by_user,
)

from app.services.counsellor_recommendation_service import (
    CounsellorRecommendationService,
)


counsellor_blueprint = Blueprint(
    "counsellors",
    __name__,
)

_recommendation_service = (
    CounsellorRecommendationService()
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
    Display available counsellors together with a transparent,
    non-diagnostic recommendation based on recent mood patterns.
    """

    access_response = user_access_required()

    if access_response is not None:
        return access_response

    counsellors = get_available_counsellors()

    weekly_summary = (
        get_weekly_mood_summary_by_user(
            session["user_id"]
        )
    )

    recommendation = (
        _recommendation_service.recommend(
            counsellors=counsellors,
            weekly_summary=weekly_summary,
        )
    )

    return render_template(
        "counsellors.html",
        counsellors=(
            recommendation[
                "recommendations"
            ]
        ),
        recommendation=recommendation,
    )


@counsellor_blueprint.route(
    "/counsellors/<int:profile_id>/book",
    methods=["GET", "POST"],
)
def book_appointment(profile_id: int):
    """
    Display available appointment slots and allow
    the user to reserve one slot.
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

    available_slots = get_available_slots_for_profile(
        profile_id
    )

    if request.method == "POST":

        slot_id_text = request.form.get(
            "availability_slot_id",
            "",
        ).strip()

        try:
            slot_id = int(slot_id_text)

        except (TypeError, ValueError):
            flash(
                "Please select an available appointment time.",
                "error",
            )

            return render_template(
                "book_appointment.html",
                counsellor=counsellor,
                available_slots=available_slots,
            )

        valid_slot_ids = {
            slot["id"]
            for slot in available_slots
        }

        if slot_id not in valid_slot_ids:
            flash(
                "That appointment time is no longer available. "
                "Please select another slot.",
                "error",
            )

            available_slots = (
                get_available_slots_for_profile(
                    profile_id
                )
            )

            return render_template(
                "book_appointment.html",
                counsellor=counsellor,
                available_slots=available_slots,
            )

        appointment_id = create_appointment_from_slot(
            user_id=session["user_id"],
            availability_slot_id=slot_id,
        )

        if appointment_id is None:
            flash(
                "That appointment time is no longer available. "
                "Please select another slot.",
                "error",
            )

            available_slots = (
                get_available_slots_for_profile(
                    profile_id
                )
            )

            return render_template(
                "book_appointment.html",
                counsellor=counsellor,
                available_slots=available_slots,
            )

        flash(
            "Appointment request submitted successfully. "
            f"Reference #{appointment_id}.",
            "success",
        )

        return redirect(
            url_for(
                "appointments.my_appointments"
            )
        )

    return render_template(
        "book_appointment.html",
        counsellor=counsellor,
        available_slots=available_slots,
    )
