from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.services.authentication_service import (
    authenticate_user,
    register_user,
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