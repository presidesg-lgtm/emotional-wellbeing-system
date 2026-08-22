from pathlib import Path
from uuid import uuid4

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from werkzeug.utils import secure_filename

from app.repositories.payment_repository import (
    create_payment_proof,
    find_payment_proof_by_appointment,
    get_appointment_for_payment,
)


payment_blueprint = Blueprint(
    "payments",
    __name__,
)


ALLOWED_PAYMENT_EXTENSIONS = {
    "pdf",
    "png",
    "jpg",
    "jpeg",
}


def allowed_payment_file(filename: str):
    """
    Return True when the uploaded file uses
    an allowed payment-proof extension.
    """

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1,
    )[1].lower()

    return extension in ALLOWED_PAYMENT_EXTENSIONS


@payment_blueprint.route(
    "/appointments/<int:appointment_id>/payment",
    methods=["GET", "POST"],
)
def submit_payment_proof(
    appointment_id: int,
):
    """
    Allow an authenticated normal user to submit
    one payment proof for their own appointment.
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

    appointment = get_appointment_for_payment(
        appointment_id=appointment_id,
        user_id=user_id,
    )

    if appointment is None:
        flash(
            "The requested appointment could not be found.",
            "error",
        )

        return redirect(
            url_for(
                "appointments.my_appointments"
            )
        )

    if appointment["status"] in {
        "cancelled",
        "rejected",
    }:
        flash(
            "Payment proof cannot be submitted "
            "for this appointment.",
            "error",
        )

        return redirect(
            url_for(
                "appointments.my_appointments"
            )
        )

    existing_payment = (
        find_payment_proof_by_appointment(
            appointment_id
        )
    )

    if existing_payment is not None:
        flash(
            "A payment proof has already been "
            "submitted for this appointment.",
            "error",
        )

        return redirect(
            url_for(
                "appointments.my_appointments"
            )
        )

    if request.method == "POST":
        uploaded_file = request.files.get(
            "payment_proof"
        )

        if (
            uploaded_file is None
            or not uploaded_file.filename
        ):
            flash(
                "Please select a payment proof file.",
                "error",
            )

            return render_template(
                "submit_payment_proof.html",
                appointment=appointment,
            )

        if not allowed_payment_file(
            uploaded_file.filename
        ):
            flash(
                "Only PDF, PNG, JPG, and JPEG files "
                "are allowed.",
                "error",
            )

            return render_template(
                "submit_payment_proof.html",
                appointment=appointment,
            )

        original_filename = secure_filename(
            uploaded_file.filename
        )

        extension = original_filename.rsplit(
            ".",
            1,
        )[1].lower()

        stored_filename = (
            f"{uuid4().hex}.{extension}"
        )

        upload_directory = Path(
            "uploads/payment_proofs"
        )

        upload_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path = (
            upload_directory
            / stored_filename
        )

        uploaded_file.save(
            file_path
        )

        payment_proof_id = create_payment_proof(
            appointment_id=appointment_id,
            user_id=user_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
        )

        flash(
            "Payment proof submitted successfully. "
            f"Reference #{payment_proof_id}.",
            "success",
        )

        return redirect(
            url_for(
                "appointments.my_appointments"
            )
        )

    return render_template(
        "submit_payment_proof.html",
        appointment=appointment,
    )