from flask import (
    Blueprint,
    redirect,
    render_template,
    session,
    url_for,
)

from app.repositories.appointment_repository import (
    get_appointments_by_user,
    get_upcoming_appointment_reminders,
)

from app.repositories.payment_repository import (
    get_payment_proofs_by_user,
)


appointment_blueprint = Blueprint(
    "appointments",
    __name__,
)


@appointment_blueprint.get("/appointments")
def my_appointments():
    """
    Display appointment requests, automatic reminders,
    and payment-proof information belonging to the
    authenticated user.
    """

    if "user_id" not in session:
        return redirect(
            url_for("auth.login")
        )

    if session.get("role") != "user":
        return redirect(
            url_for("index")
        )

    user_id = session["user_id"]

    appointments = get_appointments_by_user(
        user_id
    )

    appointment_reminders = (
        get_upcoming_appointment_reminders(
            user_id=user_id,
            reminder_hours=48,
        )
    )

    payment_proofs = get_payment_proofs_by_user(
        user_id
    )

    payment_proofs_by_appointment = {
        payment_proof["appointment_id"]: payment_proof
        for payment_proof in payment_proofs
    }

    return render_template(
        "appointments.html",
        appointments=appointments,
        appointment_reminders=appointment_reminders,
        payment_proofs=payment_proofs_by_appointment,
    )