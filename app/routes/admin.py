import csv
from io import StringIO
from pathlib import Path

from flask import (
    Blueprint,
    Response,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from werkzeug.security import generate_password_hash


from app.repositories.analytics_repository import (
    get_admin_appointment_status_distribution,
    get_admin_counsellor_workload,
    get_admin_emotion_distribution,
    get_admin_engagement_summary,
    get_admin_recent_activity,
    get_admin_system_overview,
)

from app.repositories.appointment_repository import (
    get_all_appointments_for_admin,
)

from app.repositories.counsellor_repository import (
    assign_counsellor_to_user,
    create_counsellor_account,
    get_all_counsellors_for_admin,
    get_user_counsellor_assignments,
    remove_counsellor_assignment,
    update_counsellor_account,
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
    create_user,
    find_user_by_email,
    find_user_by_id,
    get_all_users,
    get_normal_users_for_admin,
    get_user_statistics,
    update_admin_managed_user,
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



@admin_blueprint.get("/analytics")
def analytics():
    """
    Display privacy-aware aggregate system analytics
    and engagement reporting.
    """

    access_response = admin_access_required()

    if access_response is not None:
        return access_response

    return render_template(
        "admin_analytics.html",
        overview=get_admin_system_overview(),
        engagement=get_admin_engagement_summary(),
        emotion_distribution=get_admin_emotion_distribution(),
        appointment_statuses=(
            get_admin_appointment_status_distribution()
        ),
        counsellor_workload=get_admin_counsellor_workload(),
        recent_activity=get_admin_recent_activity(),
    )


@admin_blueprint.get("/analytics/report.csv")
def download_analytics_report():
    """
    Generate a downloadable aggregate CSV analytics report.

    The export contains no submitted emotional-analysis text.
    """

    access_response = admin_access_required()

    if access_response is not None:
        return access_response

    overview = get_admin_system_overview()
    engagement = get_admin_engagement_summary()
    emotion_distribution = get_admin_emotion_distribution()
    appointment_statuses = (
        get_admin_appointment_status_distribution()
    )
    counsellor_workload = get_admin_counsellor_workload()
    recent_activity = get_admin_recent_activity()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(
        [
            "Emotional Wellbeing Analysis System",
            "Administrator Analytics Report",
        ]
    )
    writer.writerow([])

    writer.writerow(["System Overview"])
    writer.writerow(["Metric", "Value"])

    overview_labels = {
        "total_analyses": "Total mood analyses",
        "users_with_mood_analyses": "Users with mood analyses",
        "total_appointments": "Total appointments",
        "users_with_appointments": "Users with appointments",
        "pending_appointments": "Pending appointments",
        "confirmed_appointments": "Confirmed appointments",
        "completed_appointments": "Completed appointments",
        "rejected_appointments": "Rejected appointments",
        "cancelled_appointments": "Cancelled appointments",
        "total_forum_posts": "Total forum posts",
        "users_with_forum_posts": "Users with forum posts",
        "visible_forum_posts": "Visible forum posts",
        "hidden_forum_posts": "Hidden forum posts",
        "total_forum_reports": "Total forum reports",
        "pending_forum_reports": "Pending forum reports",
        "total_assignments": "Current counsellor assignments",
    }

    for key, label in overview_labels.items():
        writer.writerow(
            [
                label,
                overview[key],
            ]
        )

    writer.writerow([])
    writer.writerow(["User Engagement"])
    writer.writerow(["Metric", "Value"])

    engagement_labels = {
        "total_normal_users": "Total normal users",
        "active_normal_users": "Active normal users",
        "engaged_users": "Engaged users",
        "engagement_rate": "Engagement rate (%)",
        "mood_analyses_last_7_days": "Mood analyses - last 7 days",
        "appointments_last_7_days": "Appointments - last 7 days",
        "forum_posts_last_7_days": "Forum posts - last 7 days",
    }

    for key, label in engagement_labels.items():
        writer.writerow(
            [
                label,
                engagement[key],
            ]
        )

    writer.writerow([])
    writer.writerow(["Aggregate Emotion Distribution"])
    writer.writerow(["Emotion", "Count", "Percentage"])

    for item in emotion_distribution:
        writer.writerow(
            [
                item["emotion"],
                item["count"],
                item["percentage"],
            ]
        )

    writer.writerow([])
    writer.writerow(["Appointment Status Distribution"])
    writer.writerow(["Status", "Count", "Percentage"])

    for item in appointment_statuses:
        writer.writerow(
            [
                item["status"],
                item["count"],
                item["percentage"],
            ]
        )

    writer.writerow([])
    writer.writerow(["Counsellor Workload"])
    writer.writerow(
        [
            "Counsellor",
            "Specialization",
            "Total appointments",
            "Pending",
            "Confirmed",
            "Completed",
            "Assigned users",
        ]
    )

    for counsellor in counsellor_workload:
        writer.writerow(
            [
                counsellor["counsellor_name"],
                counsellor["specialization"],
                counsellor["total_appointments"],
                counsellor["pending_appointments"],
                counsellor["confirmed_appointments"],
                counsellor["completed_appointments"],
                counsellor["assigned_users"],
            ]
        )

    writer.writerow([])
    writer.writerow(["Recent Platform Activity"])
    writer.writerow(
        [
            "Date",
            "Mood analyses",
            "Appointments created",
            "Forum posts",
        ]
    )

    for activity in recent_activity:
        writer.writerow(
            [
                activity["activity_date"].isoformat(),
                activity["mood_analyses"],
                activity["appointments"],
                activity["forum_posts"],
            ]
        )

    writer.writerow([])
    writer.writerow(
        [
            "Privacy note",
            (
                "This aggregate report does not include users' "
                "submitted emotional-analysis text."
            ),
        ]
    )

    response = Response(
        output.getvalue(),
        mimetype="text/csv",
    )

    response.headers[
        "Content-Disposition"
    ] = (
        "attachment; "
        "filename=admin-analytics-report.csv"
    )

    return response



@admin_blueprint.get("/management")
def management():
    """
    Display administrator user, counsellor,
    assignment, and session management.
    """

    access_response = admin_access_required()

    if access_response is not None:
        return access_response

    return render_template(
        "admin_management.html",
        normal_users=get_normal_users_for_admin(),
        counsellors=get_all_counsellors_for_admin(),
        assignments=get_user_counsellor_assignments(),
        appointments=get_all_appointments_for_admin(),
    )


@admin_blueprint.post("/management/users/create")
def create_normal_user():
    """Create a normal user account from the admin portal."""

    access_response = admin_access_required()
    if access_response is not None:
        return access_response

    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not full_name or not email or not password:
        flash("Name, email, and password are required.", "error")
        return redirect(url_for("admin.management"))

    if len(password) < 8:
        flash("Password must contain at least 8 characters.", "error")
        return redirect(url_for("admin.management"))

    if find_user_by_email(email) is not None:
        flash("An account already uses that email address.", "error")
        return redirect(url_for("admin.management"))

    create_user(
        full_name=full_name,
        email=email,
        password_hash=generate_password_hash(password),
        role="user",
    )

    flash("User account created successfully.", "success")
    return redirect(url_for("admin.management"))


@admin_blueprint.post("/management/users/<int:user_id>/update")
def update_normal_user(user_id: int):
    """Update a normal user's name and email."""

    access_response = admin_access_required()
    if access_response is not None:
        return access_response

    target_user = find_user_by_id(user_id)

    if target_user is None or target_user["role"] != "user":
        flash("The selected normal user could not be found.", "error")
        return redirect(url_for("admin.management"))

    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip().lower()

    if not full_name or not email:
        flash("Name and email are required.", "error")
        return redirect(url_for("admin.management"))

    existing = find_user_by_email(email)
    if existing is not None and existing["id"] != user_id:
        flash("Another account already uses that email address.", "error")
        return redirect(url_for("admin.management"))

    updated = update_admin_managed_user(
        user_id=user_id,
        full_name=full_name,
        email=email,
    )

    flash(
        "User account updated successfully."
        if updated
        else "User account could not be updated.",
        "success" if updated else "error",
    )

    return redirect(url_for("admin.management"))


@admin_blueprint.post("/management/counsellors/create")
def create_counsellor():
    """Create a counsellor account and professional profile."""

    access_response = admin_access_required()
    if access_response is not None:
        return access_response

    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    specialization = request.form.get("specialization", "").strip()
    qualifications = request.form.get("qualifications", "").strip()
    bio = request.form.get("bio", "").strip()
    years_text = request.form.get("years_experience", "0").strip()
    is_available = request.form.get("is_available") == "on"

    if not full_name or not email or not password or not specialization:
        flash(
            "Name, email, password, and specialization are required.",
            "error",
        )
        return redirect(url_for("admin.management"))

    if len(password) < 8:
        flash("Password must contain at least 8 characters.", "error")
        return redirect(url_for("admin.management"))

    try:
        years_experience = int(years_text)
    except ValueError:
        years_experience = -1

    if years_experience < 0 or years_experience > 80:
        flash("Years of experience must be between 0 and 80.", "error")
        return redirect(url_for("admin.management"))

    if find_user_by_email(email) is not None:
        flash("An account already uses that email address.", "error")
        return redirect(url_for("admin.management"))

    create_counsellor_account(
        full_name=full_name,
        email=email,
        password_hash=generate_password_hash(password),
        specialization=specialization,
        qualifications=qualifications or None,
        bio=bio or None,
        years_experience=years_experience,
        is_available=is_available,
    )

    flash("Counsellor account created successfully.", "success")
    return redirect(url_for("admin.management"))


@admin_blueprint.post(
    "/management/counsellors/<int:profile_id>/update"
)
def update_counsellor(profile_id: int):
    """Update counsellor account and profile details."""

    access_response = admin_access_required()
    if access_response is not None:
        return access_response

    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    specialization = request.form.get("specialization", "").strip()
    qualifications = request.form.get("qualifications", "").strip()
    bio = request.form.get("bio", "").strip()
    years_text = request.form.get("years_experience", "0").strip()
    is_available = request.form.get("is_available") == "on"
    counsellor_user_id = request.form.get("counsellor_user_id", type=int)

    if (
        not full_name
        or not email
        or not specialization
        or counsellor_user_id is None
    ):
        flash("Name, email, and specialization are required.", "error")
        return redirect(url_for("admin.management"))

    try:
        years_experience = int(years_text)
    except ValueError:
        years_experience = -1

    if years_experience < 0 or years_experience > 80:
        flash("Years of experience must be between 0 and 80.", "error")
        return redirect(url_for("admin.management"))

    existing = find_user_by_email(email)
    if existing is not None and existing["id"] != counsellor_user_id:
        flash("Another account already uses that email address.", "error")
        return redirect(url_for("admin.management"))

    updated = update_counsellor_account(
        profile_id=profile_id,
        full_name=full_name,
        email=email,
        specialization=specialization,
        qualifications=qualifications or None,
        bio=bio or None,
        years_experience=years_experience,
        is_available=is_available,
    )

    flash(
        "Counsellor account updated successfully."
        if updated
        else "Counsellor account could not be updated.",
        "success" if updated else "error",
    )

    return redirect(url_for("admin.management"))


@admin_blueprint.post("/management/assignments")
def assign_counsellor():
    """Assign or reassign a counsellor to an active user."""

    access_response = admin_access_required()
    if access_response is not None:
        return access_response

    user_id = request.form.get("user_id", type=int)
    counsellor_profile_id = request.form.get(
        "counsellor_profile_id",
        type=int,
    )
    support_requirement = request.form.get(
        "support_requirement",
        "",
    ).strip()

    if user_id is None or counsellor_profile_id is None:
        flash("Please select both a user and a counsellor.", "error")
        return redirect(url_for("admin.management"))

    if len(support_requirement) > 255:
        flash("Support requirement must not exceed 255 characters.", "error")
        return redirect(url_for("admin.management"))

    assigned = assign_counsellor_to_user(
        user_id=user_id,
        counsellor_profile_id=counsellor_profile_id,
        assigned_by_admin_id=session["user_id"],
        support_requirement=support_requirement or None,
    )

    flash(
        "Counsellor assigned successfully."
        if assigned
        else "Counsellor assignment could not be completed.",
        "success" if assigned else "error",
    )

    return redirect(url_for("admin.management"))


@admin_blueprint.post(
    "/management/assignments/<int:user_id>/remove"
)
def remove_assignment(user_id: int):
    """Remove a user's current counsellor assignment."""

    access_response = admin_access_required()
    if access_response is not None:
        return access_response

    removed = remove_counsellor_assignment(user_id)

    flash(
        "Counsellor assignment removed successfully."
        if removed
        else "No counsellor assignment was found.",
        "success" if removed else "error",
    )

    return redirect(url_for("admin.management"))

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
        request.referrer
        or url_for("admin.dashboard")
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
