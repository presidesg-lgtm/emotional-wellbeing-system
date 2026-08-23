from app.repositories.database import get_database_connection


def find_user_by_email(email: str):
    """
    Return a user record matching the supplied email address,
    or None when no user exists.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            id,
            full_name,
            email,
            password_hash,
            role,
            is_active,
            created_at,
            updated_at
        FROM users
        WHERE email = %s
        LIMIT 1
        """,
        (email,),
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    return user


def find_user_by_id(user_id: int):
    """
    Return a user record matching the supplied user ID,
    or None when no user exists.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            id,
            full_name,
            email,
            password_hash,
            role,
            is_active,
            created_at,
            updated_at
        FROM users
        WHERE id = %s
        LIMIT 1
        """,
        (user_id,),
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    return user


def create_user(
    full_name: str,
    email: str,
    password_hash: str,
    role: str = "user",
):
    """
    Insert a new user into the database.
    """

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO users (
            full_name,
            email,
            password_hash,
            role
        )
        VALUES (%s, %s, %s, %s)
        """,
        (
            full_name,
            email,
            password_hash,
            role,
        ),
    )

    connection.commit()

    user_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return user_id


def update_user_profile_details(
    user_id: int,
    full_name: str,
    email: str,
):
    """
    Update the editable personal profile fields
    belonging to a user account.
    """

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE users
        SET
            full_name = %s,
            email = %s
        WHERE id = %s
        """,
        (
            full_name,
            email,
            user_id,
        ),
    )

    connection.commit()

    affected_rows = cursor.rowcount

    cursor.close()
    connection.close()

    return affected_rows > 0


def update_user_password(
    user_id: int,
    password_hash: str,
):
    """
    Replace the stored password hash for a user account.
    """

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE users
        SET
            password_hash = %s
        WHERE id = %s
        """,
        (
            password_hash,
            user_id,
        ),
    )

    connection.commit()

    affected_rows = cursor.rowcount

    cursor.close()
    connection.close()

    return affected_rows > 0


def get_all_users():
    """
    Return all registered accounts for administrator review.

    Password hashes are deliberately excluded from this query.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            id,
            full_name,
            email,
            role,
            is_active,
            created_at,
            updated_at
        FROM users
        ORDER BY created_at DESC, id DESC
        """
    )

    users = cursor.fetchall()

    cursor.close()
    connection.close()

    return users




def get_normal_users_for_admin():
    """
    Return normal user accounts for administrator
    management and counsellor assignment.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            id,
            full_name,
            email,
            is_active,
            created_at,
            updated_at
        FROM users
        WHERE role = 'user'
        ORDER BY full_name ASC, id ASC
        """
    )

    users = cursor.fetchall()

    cursor.close()
    connection.close()

    return users


def update_admin_managed_user(
    user_id: int,
    full_name: str,
    email: str,
):
    """
    Update a normal user account from the administrator area.
    The account role is intentionally unchanged.
    """

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE users
        SET
            full_name = %s,
            email = %s
        WHERE
            id = %s
            AND role = 'user'
        """,
        (
            full_name,
            email,
            user_id,
        ),
    )

    connection.commit()

    updated = cursor.rowcount > 0

    cursor.close()
    connection.close()

    return updated

def get_user_statistics():
    """
    Return aggregate account statistics for the admin dashboard.
    """

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            COUNT(*) AS total_accounts,

            SUM(
                CASE
                    WHEN is_active = TRUE
                    THEN 1
                    ELSE 0
                END
            ) AS active_accounts,

            SUM(
                CASE
                    WHEN role = 'user'
                    THEN 1
                    ELSE 0
                END
            ) AS user_accounts,

            SUM(
                CASE
                    WHEN role = 'counsellor'
                    THEN 1
                    ELSE 0
                END
            ) AS counsellor_accounts,

            SUM(
                CASE
                    WHEN role = 'admin'
                    THEN 1
                    ELSE 0
                END
            ) AS admin_accounts
        FROM users
        """
    )

    statistics = cursor.fetchone()

    cursor.close()
    connection.close()

    return {
        "total_accounts": int(
            statistics["total_accounts"] or 0
        ),
        "active_accounts": int(
            statistics["active_accounts"] or 0
        ),
        "user_accounts": int(
            statistics["user_accounts"] or 0
        ),
        "counsellor_accounts": int(
            statistics["counsellor_accounts"] or 0
        ),
        "admin_accounts": int(
            statistics["admin_accounts"] or 0
        ),
    }


def update_user_active_status(
    user_id: int,
    is_active: bool,
):
    """
    Activate or deactivate a user account.
    """

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE users
        SET
            is_active = %s
        WHERE id = %s
        """,
        (
            is_active,
            user_id,
        ),
    )

    connection.commit()

    affected_rows = cursor.rowcount

    cursor.close()
    connection.close()

    return affected_rows > 0
