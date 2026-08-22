from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from mysql.connector import IntegrityError

from app.repositories.forum_repository import (
    create_forum_post,
    create_forum_report,
    get_forum_post_by_id,
    get_visible_forum_posts,
    has_user_reported_post,
)


forum_blueprint = Blueprint(
    "forum",
    __name__,
)


def normal_user_access_required():
    """
    Ensure the current session belongs
    to an authenticated normal user.
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


@forum_blueprint.route(
    "/forum",
    methods=["GET", "POST"],
)
def forum_home():
    """
    Display visible community posts and allow
    normal users to submit a new forum post.
    """

    access_response = normal_user_access_required()

    if access_response is not None:
        return access_response

    if request.method == "POST":
        content = request.form.get(
            "content",
            "",
        ).strip()

        if not content:
            flash(
                "Forum post cannot be empty.",
                "error",
            )

            return redirect(
                url_for("forum.forum_home")
            )

        if len(content) > 1000:
            flash(
                "Forum posts must not exceed 1000 characters.",
                "error",
            )

            return redirect(
                url_for("forum.forum_home")
            )

        post_id = create_forum_post(
            user_id=session["user_id"],
            content=content,
        )

        flash(
            "Forum post created successfully. "
            f"Post #{post_id}.",
            "success",
        )

        return redirect(
            url_for("forum.forum_home")
        )

    posts = get_visible_forum_posts()

    return render_template(
        "forum.html",
        posts=posts,
    )


@forum_blueprint.route(
    "/forum/<int:post_id>/report",
    methods=["GET", "POST"],
)
def report_post(post_id: int):
    """
    Allow a normal user to report a visible
    forum post for administrator review.
    """

    access_response = normal_user_access_required()

    if access_response is not None:
        return access_response

    post = get_forum_post_by_id(
        post_id
    )

    if (
        post is None
        or post["is_hidden"]
    ):
        flash(
            "The requested forum post could not be found.",
            "error",
        )

        return redirect(
            url_for("forum.forum_home")
        )

    if post["user_id"] == session["user_id"]:
        flash(
            "You cannot report your own forum post.",
            "error",
        )

        return redirect(
            url_for("forum.forum_home")
        )

    if has_user_reported_post(
        post_id=post_id,
        user_id=session["user_id"],
    ):
        flash(
            "You have already reported this post.",
            "error",
        )

        return redirect(
            url_for("forum.forum_home")
        )

    if request.method == "POST":
        reason = request.form.get(
            "reason",
            "",
        ).strip()

        if not reason:
            flash(
                "Please provide a reason for the report.",
                "error",
            )

            return render_template(
                "report_forum_post.html",
                post=post,
            )

        if len(reason) > 255:
            flash(
                "Report reason must not exceed 255 characters.",
                "error",
            )

            return render_template(
                "report_forum_post.html",
                post=post,
            )

        try:
            report_id = create_forum_report(
                post_id=post_id,
                reported_by_user_id=session["user_id"],
                reason=reason,
            )

        except IntegrityError:
            flash(
                "You have already reported this post.",
                "error",
            )

            return redirect(
                url_for("forum.forum_home")
            )

        flash(
            "Forum post reported successfully. "
            f"Report #{report_id}.",
            "success",
        )

        return redirect(
            url_for("forum.forum_home")
        )

    return render_template(
        "report_forum_post.html",
        post=post,
    )