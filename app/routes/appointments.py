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


appointment_blueprint = Blueprint(
    "appointments",
    __name__,
)


@appointment_blueprint.get("/appointments")
def my_appointments():
    """
    Display appointment requests belonging
    to the authenticated normal user.
    """

    if "user_id" not in session:
        return redirect(
            url_for("auth.login")
        )

    if session.get("role") != "user":
        return redirect(
            url_for("index")
        )

    appointments = get_appointments_by_user(
        session["user_id"]
    )

    return render_template(
        "appointments.html",
        appointments=appointments,
    )