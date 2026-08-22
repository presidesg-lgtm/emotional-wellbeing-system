from flask import (
    Blueprint,
    redirect,
    render_template,
    session,
    url_for,
)

from app.repositories.appointment_repository import (
    get_appointments_by_user,
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
    Display appointment requests and payment-proof
    information belonging to the authenticated user.
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
        payment_proofs=payment_proofs_by_appointment,
    )