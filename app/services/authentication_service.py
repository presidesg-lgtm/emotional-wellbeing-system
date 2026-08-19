from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from app.repositories.user_repository import (
    create_user,
    find_user_by_email,
)


def register_user(
    full_name: str,
    email: str,
    password: str,
):
    """
    Validate registration details, hash the password,
    and create a normal user account.
    """

    cleaned_name = full_name.strip()
    cleaned_email = email.strip().lower()

    if not cleaned_name:
        raise ValueError("Full name is required.")

    if not cleaned_email:
        raise ValueError("Email address is required.")

    if "@" not in cleaned_email:
        raise ValueError("Please enter a valid email address.")

    if len(password) < 8:
        raise ValueError(
            "Password must contain at least 8 characters."
        )

    existing_user = find_user_by_email(
        cleaned_email
    )

    if existing_user is not None:
        raise ValueError(
            "An account already exists with this email address."
        )

    password_hash = generate_password_hash(
        password
    )

    user_id = create_user(
        full_name=cleaned_name,
        email=cleaned_email,
        password_hash=password_hash,
        role="user",
    )

    return {
        "id": user_id,
        "full_name": cleaned_name,
        "email": cleaned_email,
        "role": "user",
    }


def register_admin(
    full_name: str,
    email: str,
    password: str,
):
    """
    Validate administrator details, hash the password,
    and create a new admin account.
    """

    cleaned_name = full_name.strip()
    cleaned_email = email.strip().lower()

    if not cleaned_name:
        raise ValueError("Full name is required.")

    if not cleaned_email:
        raise ValueError("Email address is required.")

    if "@" not in cleaned_email:
        raise ValueError("Please enter a valid email address.")

    if len(password) < 8:
        raise ValueError(
            "Password must contain at least 8 characters."
        )

    existing_user = find_user_by_email(
        cleaned_email
    )

    if existing_user is not None:
        raise ValueError(
            "An account already exists with this email address."
        )

    password_hash = generate_password_hash(
        password
    )

    user_id = create_user(
        full_name=cleaned_name,
        email=cleaned_email,
        password_hash=password_hash,
        role="admin",
    )

    return {
        "id": user_id,
        "full_name": cleaned_name,
        "email": cleaned_email,
        "role": "admin",
    }


def authenticate_user(
    email: str,
    password: str,
):
    """
    Validate user login credentials.
    """

    cleaned_email = email.strip().lower()

    user = find_user_by_email(
        cleaned_email
    )

    if user is None:
        return None

    if not user["is_active"]:
        return None

    if not check_password_hash(
        user["password_hash"],
        password,
    ):
        return None

    return user