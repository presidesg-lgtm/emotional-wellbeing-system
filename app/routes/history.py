from flask import Blueprint, redirect, render_template, session, url_for

from app.repositories.mood_repository import get_mood_entries_by_user


history_blueprint = Blueprint(
    "history",
    __name__,
)


@history_blueprint.get("/history")
def mood_history():
    """
    Display the authenticated user's emotion-analysis history.
    """

    if "user_id" not in session:
        return redirect(
            url_for("auth.login")
        )

    mood_entries = get_mood_entries_by_user(
        session["user_id"]
    )

    return render_template(
        "history.html",
        mood_entries=mood_entries,
    )