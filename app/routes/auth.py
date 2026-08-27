from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.repositories.user_repository import (
    find_user_by_id,
)

from app.services.authentication_service import (
    authenticate_user,
    change_user_password,
    register_user,
    update_profile,
)


auth_blueprint = Blueprint(
    "auth",
    __name__,
)


@auth_blueprint.route(
    "/register",
    methods=["GET", "POST"],
)
def register():
    """
    Display the registration form and create a normal user account.
    """

    if request.method == "POST":
        full_name = request.form.get(
            "full_name",
            "",
        )

        email = request.form.get(
            "email",
            "",
        )

        password = request.form.get(
            "password",
            "",
        )

        confirm_password = request.form.get(
            "confirm_password",
            "",
        )

        if password != confirm_password:
            flash(
                "Passwords do not match.",
                "error",
            )

            return render_template(
                "register.html"
            )

        try:
            register_user(
                full_name=full_name,
                email=email,
                password=password,
            )

        except ValueError as error:
            flash(
                str(error),
                "error",
            )

            return render_template(
                "register.html"
            )

        flash(
            "Account created successfully. "
            "You can now log in.",
            "success",
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "register.html"
    )


@auth_blueprint.route(
    "/login",
    methods=["GET", "POST"],
)
def login():
    """
    Authenticate the account, create a session,
    and redirect according to the user's role.
    """

    if request.method == "POST":
        email = request.form.get(
            "email",
            "",
        )

        password = request.form.get(
            "password",
            "",
        )

        user = authenticate_user(
            email,
            password,
        )

        if user is None:
            flash(
                "Invalid email or password.",
                "error",
            )

            return render_template(
                "login.html"
            )

        session.clear()

        session["user_id"] = user["id"]
        session["full_name"] = user["full_name"]
        session["role"] = user["role"]
        session.permanent = True

        if user["role"] == "admin":
            return redirect(
                url_for("admin.dashboard")
            )

        if user["role"] == "counsellor":
            return redirect(
                url_for("counsellor_portal.dashboard")
            )

        return redirect(
            url_for("index")
        )

    return render_template(
        "login.html"
    )


@auth_blueprint.route(
    "/profile",
    methods=["GET", "POST"],
)
def profile():
    """
    Allow authenticated normal users to view and
    update their own profile information.
    """

    if not session.get("user_id"):
        flash(
            "Please log in to access your profile.",
            "error",
        )

        return redirect(
            url_for("auth.login")
        )

    if session.get("role") != "user":
        flash(
            "Profile management is available to normal user accounts.",
            "error",
        )

        return redirect(
            url_for("index")
        )

    user_id = session["user_id"]

    user = find_user_by_id(
        user_id
    )

    if user is None:
        session.clear()

        flash(
            "Your account could not be found. Please log in again.",
            "error",
        )

        return redirect(
            url_for("auth.login")
        )

    if request.method == "POST":
        action = request.form.get(
            "action",
            "",
        )

        if action == "update_profile":
            full_name = request.form.get(
                "full_name",
                "",
            )

            email = request.form.get(
                "email",
                "",
            )

            try:
                updated_profile = update_profile(
                    user_id=user_id,
                    full_name=full_name,
                    email=email,
                )

            except ValueError as error:
                flash(
                    str(error),
                    "error",
                )

            else:
                session["full_name"] = (
                    updated_profile["full_name"]
                )

                flash(
                    "Profile updated successfully.",
                    "success",
                )

                return redirect(
                    url_for("auth.profile")
                )

        elif action == "change_password":
            current_password = request.form.get(
                "current_password",
                "",
            )

            new_password = request.form.get(
                "new_password",
                "",
            )

            confirm_password = request.form.get(
                "confirm_password",
                "",
            )

            try:
                change_user_password(
                    user_id=user_id,
                    current_password=current_password,
                    new_password=new_password,
                    confirm_password=confirm_password,
                )

            except ValueError as error:
                flash(
                    str(error),
                    "error",
                )

            else:
                flash(
                    "Password changed successfully.",
                    "success",
                )

                return redirect(
                    url_for("auth.profile")
                )

        else:
            flash(
                "Invalid profile action.",
                "error",
            )

        user = find_user_by_id(
            user_id
        )

    return render_template(
        "profile.html",
        user=user,
    )


@auth_blueprint.post("/logout")
def logout():
    """
    Clear the authenticated user's session.
    """

    session.clear()

    flash(
        "You have been logged out.",
        "success",
    )

    return redirect(
        url_for("auth.login")
    )