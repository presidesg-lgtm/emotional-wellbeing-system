from flask import (
    Blueprint,
    redirect,
    render_template,
    session,
    url_for,
)

from app.repositories.mood_repository import (
    get_emotion_distribution_by_user,
    get_mood_entries_by_user,
    get_mood_summary_by_user,
)


dashboard_blueprint = Blueprint(
    "dashboard",
    __name__,
)


@dashboard_blueprint.get("/dashboard")
def dashboard():
    """
    Display a summary dashboard for the authenticated user.
    """

    if "user_id" not in session:
        return redirect(
            url_for("auth.login")
        )

    user_id = session["user_id"]

    summary = get_mood_summary_by_user(
        user_id
    )

    emotion_distribution = (
        get_emotion_distribution_by_user(
            user_id
        )
    )

    recent_entries = get_mood_entries_by_user(
        user_id,
        limit=5,
    )

    return render_template(
        "dashboard.html",
        summary=summary,
        recent_entries=recent_entries,
        emotion_distribution=emotion_distribution,
    )