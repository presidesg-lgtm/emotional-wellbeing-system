from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from app.repositories.user_repository import (
    create_user,
    find_user_by_email,
    find_user_by_id,
    update_user_password,
    update_user_profile_details,
)


def _validate_registration_details(
    full_name: str,
    email: str,
    password: str,
):
    """
    Validate common registration details and return
    cleaned name and email values.
    """

    cleaned_name = full_name.strip()
    cleaned_email = email.strip().lower()

    if not cleaned_name:
        raise ValueError("Full name is required.")

    if not cleaned_email:
        raise ValueError("Email address is required.")

    if "@" not in cleaned_email:
        raise ValueError(
            "Please enter a valid email address."
        )

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

    return cleaned_name, cleaned_email


def register_user(
    full_name: str,
    email: str,
    password: str,
):
    """
    Validate registration details, hash the password,
    and create a normal user account.
    """

    cleaned_name, cleaned_email = (
        _validate_registration_details(
            full_name=full_name,
            email=email,
            password=password,
        )
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

    cleaned_name, cleaned_email = (
        _validate_registration_details(
            full_name=full_name,
            email=email,
            password=password,
        )
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


def register_counsellor(
    full_name: str,
    email: str,
    password: str,
):
    """
    Validate counsellor details, hash the password,
    and create a new counsellor account.
    """

    cleaned_name, cleaned_email = (
        _validate_registration_details(
            full_name=full_name,
            email=email,
            password=password,
        )
    )

    password_hash = generate_password_hash(
        password
    )

    user_id = create_user(
        full_name=cleaned_name,
        email=cleaned_email,
        password_hash=password_hash,
        role="counsellor",
    )

    return {
        "id": user_id,
        "full_name": cleaned_name,
        "email": cleaned_email,
        "role": "counsellor",
    }


def authenticate_user(
    email: str,
    password: str,
):
    """
    Validate account login credentials.
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


def update_profile(
    user_id: int,
    full_name: str,
    email: str,
):
    """
    Validate and update the editable details
    of an existing normal user profile.
    """

    cleaned_name = full_name.strip()
    cleaned_email = email.strip().lower()

    if not cleaned_name:
        raise ValueError(
            "Full name is required."
        )

    if len(cleaned_name) > 100:
        raise ValueError(
            "Full name must not exceed 100 characters."
        )

    if not cleaned_email:
        raise ValueError(
            "Email address is required."
        )

    if "@" not in cleaned_email:
        raise ValueError(
            "Please enter a valid email address."
        )

    if len(cleaned_email) > 255:
        raise ValueError(
            "Email address is too long."
        )

    current_user = find_user_by_id(
        user_id
    )

    if current_user is None:
        raise ValueError(
            "User account could not be found."
        )

    existing_user = find_user_by_email(
        cleaned_email
    )

    if (
        existing_user is not None
        and existing_user["id"] != user_id
    ):
        raise ValueError(
            "Another account already uses this email address."
        )

    update_user_profile_details(
        user_id=user_id,
        full_name=cleaned_name,
        email=cleaned_email,
    )

    return {
        "id": user_id,
        "full_name": cleaned_name,
        "email": cleaned_email,
    }


def change_user_password(
    user_id: int,
    current_password: str,
    new_password: str,
    confirm_password: str,
):
    """
    Verify the existing password before replacing it
    with a newly generated password hash.
    """

    user = find_user_by_id(
        user_id
    )

    if user is None:
        raise ValueError(
            "User account could not be found."
        )

    if not current_password:
        raise ValueError(
            "Current password is required."
        )

    if not check_password_hash(
        user["password_hash"],
        current_password,
    ):
        raise ValueError(
            "Current password is incorrect."
        )

    if len(new_password) < 8:
        raise ValueError(
            "New password must contain at least 8 characters."
        )

    if new_password != confirm_password:
        raise ValueError(
            "New passwords do not match."
        )

    if check_password_hash(
        user["password_hash"],
        new_password,
    ):
        raise ValueError(
            "New password must be different from the current password."
        )

    new_password_hash = generate_password_hash(
        new_password
    )

    update_user_password(
        user_id=user_id,
        password_hash=new_password_hash,
    )

    return True