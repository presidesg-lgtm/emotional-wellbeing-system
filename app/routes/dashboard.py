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
    get_seven_day_mood_trend_by_user,
    get_weekly_mood_summary_by_user,
)


dashboard_blueprint = Blueprint(
    "dashboard",
    __name__,
)


@dashboard_blueprint.get("/dashboard")
def dashboard():
    """
    Display emotional-analysis summaries and recent
    time-based mood trends for the authenticated user.
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

    summary = get_mood_summary_by_user(
        user_id
    )

    weekly_summary = (
        get_weekly_mood_summary_by_user(
            user_id
        )
    )

    seven_day_trend = (
        get_seven_day_mood_trend_by_user(
            user_id
        )
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
        weekly_summary=weekly_summary,
        seven_day_trend=seven_day_trend,
        recent_entries=recent_entries,
        emotion_distribution=emotion_distribution,
    )
